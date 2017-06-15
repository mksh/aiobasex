import asyncio
import collections
import hashlib
import logging


from .errors import CannotAuthenticate


logger = logging.getLogger(__name__)


@asyncio.coroutine
def create_connection(host='127.0.0.1', port=1984, *, username=None,
                      password=None, encoding='utf-8', loop=None):
    """Create connection to baseX.

    :param host: A host, where BaseX server is listening.
    :type host: str
    :param port: A port, where BaseX server is listening.
    :type port: int
    :param encoding: An encoding to use for string to bytes (and vice-versa)
        conversion, when communicating with BaseX server.
    :type encoding: str
    :param username: A username to authenticate with.
    :type username: str
    :param password: A password to authenticate with.
    :type password: str
    :param loop: Asyncio`s event loop.
    :type loop: asyncio.BaseEventLoop
    """
    assert username, 'BaseX requires username to authenticate.'
    assert password, 'BaseX requires username to authenticate.'
    reader, writer = yield from asyncio.open_connection(host, port, loop=loop)
    connection = BaseXConnection(
        reader=reader, writer=writer, encoding=encoding,
        address=(host, port), username=username, password=password, loop=loop)
    yield from connection.wait_authenticated()
    return connection


class BaseXConnection(asyncio.Protocol):
    """Represents a single connection to BaseX server,
        and exposes methods for low-level data interchange.

    See http://docs.basex.org/wiki/Server_Protocol
        for detailed protocol description.
    """

    # A terminator symbol - null byte.
    SUCCESS_TERM = b'\x00'

    # Indicates errors.
    ERROR_TERM = b'\x01'

    def __init__(self, reader, writer, *,
                 username, password, encoding, address, loop=None):
        """BaseXConnection ctor

        :param reader: A reader for BaseX connection.
        :type reader: asyncio.streams.StreamReader
        :param writer: A writer for BaseX connection.
        :type writer: asyncio.streams.StreamWriter
        :param address: A host-port pair, to be used in string representation
                        of this BaseXConnection.
        :type address: tuple]str,int]
        :param loop: Asyncio`s event loop.
        :type loop: asyncio.BaseEventLoop
        """
        self._reader = reader
        self._writer = writer
        self._host, self._port = address
        self._loop = loop or asyncio.get_event_loop()
        self._auth_task = asyncio.Task(self._authenticate(), loop=self._loop)
        self._auth_task.add_done_callback(self._start_reader_task)
        self._reader_task = None
        self._waiters = collections.deque()
        self._username = username
        self._password = password
        self._encoding = encoding
        self._authenticated = asyncio.Future(loop=self._loop)
        self._closed = asyncio.Future(loop=self._loop)
        self._closing = False

    @property
    def loop(self):
        return self._loop

    @property
    def authenticated(self):
        return self._authenticated.done()

    def __repr__(self):
        """Gets string representation of this BaseX connection."""
        return '<BaseXConnection: {}:{}{}>'.format(
            self._host, self._port,
            ' authenticated' if self._reader_task else ''
        )

    def _start_reader_task(self, fut):
        """Start reader task in case of successful authentication.

        :param fut: A result of _read_realm() execution.
        :type fut: asyncio.Future
        """
        if not fut.exception():
            self._reader_task = asyncio.Task(
                self._read_data(), loop=self._loop)

    @asyncio.coroutine
    def _read_msg(self):
        """Read the message until the terminator is reached;
            return the message without terminator."""

        buf = b''

        while True:
            char = yield from self._reader.readexactly(1)

            if char in (self.SUCCESS_TERM, self.ERROR_TERM):
                if char == self.SUCCESS_TERM:
                    if buf and buf[-1] == b'\xFF':
                        buf = buf[:-1] + b'\x00'
                        continue
                    error = False
                    break
                elif char == self.ERROR_TERM:
                    error = True
                    break
            else:
                buf += char

        data = buf.replace(b'\xFF\xFF', b'\xFF')
        data_decoded = data.decode(self._encoding)

        return error, data_decoded

    def send_msg(self, data, waiter=None, success_term_twice=False):
        """Send the message to BaseX server.

        :param data: A data to send.
        :type data: bytes
        :param waiter: A future, resolving on BaseX response.
        :type waiter: asyncio.Future
        :param success_term_twice:Whether to wait for success terminator twice.
        :type success_term_twice: bool
        """
        if isinstance(data, str):
            data = data.encode(self._encoding)  # pragma: no cover
        self._writer.write(data)

        if waiter:
            if isinstance(waiter, list):
                for _waiter in waiter:
                    self._waiters.append((_waiter, success_term_twice))
            else:
                self._waiters.append((waiter, success_term_twice))

    @asyncio.coroutine
    def _authenticate(self):
        """Read authentication realm,
            decide which authentication type to use,
             perform auth handshake.
        """

        _, data = yield from self._read_msg()
        if ':' in data:
            # Use 'digest' authentication method.
            realm, nonce = data.split(':')
            secret_to_hash = '{username}:{realm}:{password}'.format(
                username=self._username,
                realm=realm,
                password=self._password,
            ).encode('utf-8')
        else:
            # Fall back to 'cram-md5' auth.
            nonce = data  # pragma: no cover
            secret_to_hash = self._password.encode('utf-8')  # pragma: no cover

        # Compute the client nonce value.
        secret_hash = hashlib.new('md5')
        main_hash = hashlib.new('md5')
        secret_hash.update(secret_to_hash)
        main_hash.update((secret_hash.hexdigest() + nonce).encode('utf-8'))

        username = self._username.encode('utf-8') + self.SUCCESS_TERM
        digest = main_hash.hexdigest().encode('utf-8') + self.SUCCESS_TERM

        self.send_msg(username)
        self.send_msg(digest)

        response = yield from self._reader.readexactly(1)
        if response == self.SUCCESS_TERM:
            self._authenticated.set_result(True)
        else:
            self._authenticated.set_result(False)

    @asyncio.coroutine
    def _read_data(self):
        while not self._reader.at_eof() and not self._closing:
            error, msg = yield from self._read_msg()
            if not msg and not self._waiters:
                continue

            elif not self._waiters:
                # Possible busy loop!
                while not self._waiters:
                    yield from asyncio.sleep(0)

            waiter, do_additional_read = self._waiters.popleft()

            # Some commands do send additional \x00 in results
            if do_additional_read and not error:
                yield from self._reader.readexactly(1)
            waiter.set_result((error, msg))

    @asyncio.coroutine
    def wait_authenticated(self):
        """Wait until this client authenticates."""
        result = yield from self._authenticated
        if result is False:
            raise CannotAuthenticate('Invalid username or password supplied')

    @asyncio.coroutine
    def close(self):
        """Close this connection, and cancel all waiters."""
        self._closing = True
        self._reader_task.cancel()
        self._writer.transport.close()
        self._writer = None
        self._reader = None
        self._reader_task = None
        while self._waiters:
            waiter = self._waiters.pop()
            waiter.cancel()
