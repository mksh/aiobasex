import asynctest

from aiobasex.connection import create_connection
from aiobasex.errors import CannotAuthenticate


class CreateConnectionTest(asynctest.TestCase):

    use_default_loop = True

    async def test_create_connection_bad_auth(self):

        raised = False

        try:
            await create_connection(
                'basex.docker',
                username='b@d',
                password='@uth',
                loop=self.loop
            )
        except CannotAuthenticate:
            raised = True
        finally:
            if not raised:
                self.fail('CanNotAuthenticate not raised')  # pragma: no cover

    async def test_create_connection_success(self):

        conn = await create_connection(
            'basex.docker',
            username='admin',
            password='admin',
            loop=self.loop
        )

        self.assertEqual(repr(conn), '<BaseXConnection: basex.docker:1984>')
        self.assertTrue(conn.authenticated)
