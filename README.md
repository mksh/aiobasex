## aiobasex

A non-blocking client for [BaseX](http://basex.org/), implemented on top of python asyncio.

`aiobasex` has no dependencies apart from Python standard library.

Currently all the methods of BaseX Command Protocol and Query Command Protocol are implemented, except methods `FULL`, `INFO` and `OPTIONS` of the latter.


#### Usage example

```python

from aiobasex import create_connection, BaseXSession
    
    
async def example():
    """Connects to BaseX and performs simple query."""

    # Instatiate connection, and initialize session with it.
    connection = await create_connection(host, port, username=username, password=password)
    session = BaseXSession(connection)

    # Register XQuery.
    query = await session.query('''
        declare variable $toCompute as xs:integer external;

        declare function local:factorial($N as xs:integer?) as xs:integer {
            if ($N <= 1) then
                1
            else
                $N * local:factorial($N - 1)
        };
        local:factorial($toCompute)
    ''')

    # Bind an external variable.
    await query.bind('toCompute', 8)
    
    # Execute query -> prints 40320
    print(await query.execute())
    
    # Un-register query at server.
    await query.close()
    
    # Close connection.
    await connection.close()
```


#### Testing
Invoke 

`make test`

to run the test suite. 
[Docker](https://docker.io) and [Docker Compose](https://docs.docker.com/compose/) must be installed in order to do this.

#### TODO

- connection pooling
- test coverage for pythons 3.4 and 3.6
- implement API for `FULL`, `INFO` and `OPTIONS`
- rtfd entry
- 100% test coverage, incl. negative everywhere
