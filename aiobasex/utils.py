import asyncio
import functools


def string_args_to_bytes(*arg_positions):
    """Convert positional arguments to bytes, in case if string is passed.

    Since BaseX write protocol works only with bytes, it is necessary
        to be able passing strings to API.
    """

    def wrapper(func):

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if arg_positions:
                new_args = []
                for pos, arg in enumerate(args):
                    if pos in arg_positions and isinstance(arg, str):
                        arg = arg.encode('utf-8')
                    new_args.append(arg)
                args = tuple(new_args)
            return func(*args, **kwargs)

        return wrapped

    return wrapper


def communicate_with_server(connection, to_send, *, loop,
                            success_term_twice=False):
    """Send data and wait response from the server.

    :param to_send: A bytes to send to remote end.
    :type to_send: bytes
    :param connection: A baseX connection.
    :type connection: aiobasex.BaseXConnection
    :param success_term_twice: Wait until success term arrives twice.
    :type success_term_twice: bool
    :returns: Pair of values, first containing possible error,
                second - the result of execution.
    :rtype tuple[str|None,str|None]
    """
    waiter = asyncio.Future(loop=loop)

    connection.send_msg(to_send, waiter=waiter,
                        success_term_twice=success_term_twice)

    error, result = yield from waiter

    return error, result
