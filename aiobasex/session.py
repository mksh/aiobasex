import asyncio
import logging

from aiobasex import errors, query
from aiobasex.utils import communicate_with_server, string_args_to_bytes


logger = logging.getLogger(__name__)


class BaseXSession:

    # A facade for BaseX intercommunication.
    _QUERY = b'\x00'
    _CREATE = b'\x08'
    _ADD = b'\x09'
    _REPLACE = b'\x0C'
    _STORE = b'\x0D'

    def __init__(self, connection):
        self._connection = connection
        self._loop = connection.loop

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._loop.create_task(self._connection.close())

    @string_args_to_bytes(1)
    @asyncio.coroutine
    def command(self, c):
        """Invokes BaseX command, and returns results.

        :param c: A command to execute.
        :type c: bytes
        """

        result_waiter = asyncio.Future(loop=self._loop)
        info_waiter = asyncio.Future(loop=self._loop)

        self._connection.send_msg(
            c + self._connection.SUCCESS_TERM,
            waiter=[result_waiter, info_waiter])

        r_err, r_msg = yield from result_waiter
        if r_err:
            raise errors.CommandError('Info: {!s}'.format(r_msg))
        i_err, i_msg = yield from info_waiter

        logger.info(i_msg)

        return r_msg

    def _communicate(self, to_send):
        return communicate_with_server(self._connection,
                                       to_send, loop=self._loop)

    @string_args_to_bytes(1)
    @asyncio.coroutine
    def query(self, q):
        """Creates C{BaseXQuery}"""
        error, _ = yield from self._communicate(
            self._QUERY + q + self._connection.SUCCESS_TERM)
        if error:
            raise errors.QueryError(_)
        else:
            return query.BaseXQuery(self._connection, _)

    @string_args_to_bytes(1, 2)
    @asyncio.coroutine
    def create(self, d, i=b''):
        """Creates a database.

        :param d: A name of database to create.
        :type d: bytes
        :param i: An input for database
        :type i: bytes
        :raises errors.CannotCreateDatabase: When failes to create DB.
        """
        error, _ = yield from self._communicate(
            self._CREATE + d + self._connection.SUCCESS_TERM +
            i + self._connection.SUCCESS_TERM,
        )
        if error:
            raise errors.CannotCreateDatabase(_)
        else:
            logger.info(_)

    @string_args_to_bytes(1, 2, 3)
    @asyncio.coroutine
    def add(self, p, i):
        """Creates a resource in given database at given path.

        :param d: A database name.
        :type d: bytes
        :param p: A path, where to store data.
        :type p: bytes
        :param i: A document body.
        :type i: bytes
        """
        error, _ = yield from self._communicate(
            self._ADD + p +
            self._connection.SUCCESS_TERM + i + self._connection.SUCCESS_TERM,
        )

        if error:
            raise errors.CannotAddResource(_)
        else:
            logger.info(_)

    @string_args_to_bytes(1, 2)
    @asyncio.coroutine
    def replace(self, p, i):
        """Replaces a resource at given path with given input document.

        :param p: A path to resource.
        :type p: bytes
        :param i: An input document to replace.
        :type i: bytes
        """
        error, _ = yield from self._communicate(
            self._REPLACE + p + self._connection.SUCCESS_TERM +
            i + self._connection.SUCCESS_TERM,
        )

        if error:
            raise errors.CannotReplaceResource(_)
        else:
            logger.info(_)

    @string_args_to_bytes(1, 2)
    @asyncio.coroutine
    def store(self, p, i):
        """Stores a BLOB in BaseX.

        :param p: A path, where to store BLOB.
        :type p: bytes
        :param i: An input blob.
        :type i: bytes
        """
        error, _ = yield from self._communicate(self._STORE + p +
                                                self._connection.SUCCESS_TERM +
                                                i +
                                                self._connection.SUCCESS_TERM)

        if error:
            raise errors.CannotReplaceResource(_)
        else:
            logger.info(_)
