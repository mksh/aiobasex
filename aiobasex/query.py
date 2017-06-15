import asyncio
import logging

from aiobasex import errors
from aiobasex.utils import communicate_with_server, string_args_to_bytes


logger = logging.getLogger(__name__)


class BaseXQuery:

    # Query command protocol identifiers
    _CLOSE = b'\x02'
    _BIND = b'\x03'
    _RESULTS = b'\x04'
    _EXECUTE = b'\x05'
    _INFO = b'\x06'
    _CONTEXT = b'\x0E'
    _UPDATING = b'\x1E'
    _FULL = b'\x1F'

    def __init__(self, connection, query_id):
        self._connection = connection
        self._loop = connection.loop
        self._query_id = query_id.encode('utf-8')

    def __eq__(self, other):
        return self._query_id == other.query_id

    @property
    def query_id(self):
        return self._query_id

    def _communicate(self, to_send, success_term_twice=False):
        return communicate_with_server(self._connection, to_send,
                                       loop=self._loop)

    @asyncio.coroutine
    def close(self):
        """Closes this Query."""
        error, result = yield from self._communicate(
            self._CLOSE + self._query_id + self._connection.SUCCESS_TERM,
            success_term_twice=True)
        if error:
            raise errors.QueryError(result)
        logger.info(result)

    @asyncio.coroutine
    def execute(self):
        """Executes the Query."""
        error, result = yield from self._communicate(
            self._EXECUTE + self._query_id + self._connection.SUCCESS_TERM,
            success_term_twice=True,
        )
        if error:
            raise errors.QueryError(result)
        return result

    @asyncio.coroutine
    def results(self):
        """Retrieves query results."""
        error, result = yield from self._communicate(
            self._RESULTS + self._query_id + self._connection.SUCCESS_TERM,
            success_term_twice=True)
        if error:
            raise errors.QueryError(result)
        return result[1:]

    @string_args_to_bytes(1, 2, 3)
    @asyncio.coroutine
    def bind(self, var, value, type=b''):
        """Bind variable to a query."""

        error, result = yield from self._communicate(
            self._BIND + self._query_id +
            self._connection.SUCCESS_TERM + var +
            self._connection.SUCCESS_TERM + value +
            self._connection.SUCCESS_TERM + type +
            self._connection.SUCCESS_TERM, success_term_twice=True
        )
        if error:
            raise errors.QueryError(result)
        logger.info(result)

    @string_args_to_bytes(1, 2)
    @asyncio.coroutine
    def context(self, value, type=b''):
        """Bind context variable to a query."""
        error, result = yield from self._communicate(
            self._CONTEXT + self._query_id +
            self._connection.SUCCESS_TERM + value +
            self._connection.SUCCESS_TERM + type +
            self._connection.SUCCESS_TERM, success_term_twice=True,
        )
        if error:
            raise errors.QueryError(result)
        logger.info(result)

    @asyncio.coroutine
    def updating(self):
        """Determine, if query updating."""
        error, result = yield from self._communicate(
            self._UPDATING + self._query_id + self._connection.SUCCESS_TERM,
            success_term_twice=True,
        )
        if error:
            raise errors.QueryError(result)
        return True if result == 'true' else False
