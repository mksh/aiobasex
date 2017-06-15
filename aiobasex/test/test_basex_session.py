import asynctest

from aiobasex.connection import create_connection
from aiobasex.query import BaseXQuery
from aiobasex.session import BaseXSession


class BaseXSessionTest(asynctest.TestCase):

    use_default_loop = True

    async def setUp(self):
        self._connection = await create_connection(
            'basex.docker',
            username='admin',
            password='admin',
            loop=self.loop,
        )
        self.session = BaseXSession(connection=self._connection)

    async def tearDown(self):
        await self._connection.close()

    async def test_query_create(self):
        result = await self.session.query(
            'for $i in (1 to 3) return <a> { $i } </a>')
        self.assertEqual(result, BaseXQuery(self._connection, '0'))

    async def test_db_create_add_query(self):
        await self.session.create(b'test_db')

        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")

        q = await self.session.query(b'''
            for $doc in collection("test_db")
                where matches(document-uri($doc), "test.xml")
                return $doc/xml/root/child
        ''')
        result = await q.execute()
        self.assertEqual(result, '<child/>')

    async def test_db_replace_add_query(self):

        await self.session.create(b'test_db')

        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")

        await self.session.replace(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><grandchild/></root></xml>")

        q = await self.session.query(b'''
            for $doc in collection("test_db")
                where matches(document-uri($doc), "test.xml")
                return $doc/xml/root/grandchild
        ''')
        result = await q.execute()
        self.assertEqual(result, '<grandchild/>')

    async def test_db_store_query(self):
        await self.session.create(b'test_db')

        await self.session.store(b'test.blob', b"peacelove")

        res = await self.session.command(b'RETRIEVE test.blob')

        self.assertEqual(res, 'peacelove')
