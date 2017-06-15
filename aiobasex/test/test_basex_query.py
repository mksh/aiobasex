import asynctest

from aiobasex.connection import create_connection
from aiobasex.test.utils import get_cleaned_node
from aiobasex.session import BaseXSession


class BaseXConnectionTest(asynctest.TestCase):

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

    async def test_db_replace_query(self):
        await self.session.create(b'test_db')

        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")
        q1 = await self.session.query(b'''
            let $doc := (for $doc in collection('test_db')
                    where matches(document-uri($doc), 'test.xml')
                return $doc)
            return $doc/xml/root
        ''')
        result = await q1.execute()
        self.assertEqual(
            get_cleaned_node(result),
            '<?xml version="1.0" encoding="utf-8"?><root><child/></root>')
        await q1.close()

        await self.session.replace(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><grandchild/></root></xml>")
        q2 = await self.session.query(b'''
            let $doc := (for $doc in collection('test_db')
                    where matches(document-uri($doc), 'test.xml')
                return $doc)
            return $doc/xml/root
        ''')
        result = await q2.execute()

        self.assertEqual(
            get_cleaned_node(result),
            '<?xml version="1.0" encoding="utf-8"?><root><grandchild/></root>',
        )
        await q2.close()

    async def test_query_results(self):
        await self.session.create(b'test_db')
        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")
        q1 = await self.session.query(b'''
            let $doc := (for $doc in collection('test_db')
                    where matches(document-uri($doc), 'test.xml')
                return $doc)
            return $doc/xml/root
        ''')
        results = await q1.results()
        self.assertEqual(results, '<root>\n  <child/>\n</root>')

    async def test_query_bind(self):
        await self.session.create(b'test_db')
        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")
        q1 = await self.session.query(b'''
            declare variable $bar as xs:string external;

            let $doc := (for $doc in collection('test_db')
                    where matches(document-uri($doc), 'test.xml')
                return $doc)
            return <result>$doc/xml/root<tail foo="{$bar}" /></result>
        ''')
        await q1.bind('bar', 'bar')
        result = await q1.execute()

        self.assertEqual(
            '<result>$doc/xml/root<tail foo="bar"/>\n</result>',
            result,
        )

        await q1.bind('bar', 'foo')
        result = await q1.execute()

        self.assertEqual(
            '<result>$doc/xml/root<tail foo="foo"/>\n</result>',
            result,
        )

    async def test_query_updating(self):
        await self.session.create(b'test_db')
        await self.session.add(
            b'test.xml',
            b"<?xml version='1.0' encoding='utf-8'?>"
            b"<xml><root><child/></root></xml>")

        q1 = await self.session.query(b'''
            declare variable $bar as xs:string external;

            let $doc := (for $doc in collection('test_db')
                    where matches(document-uri($doc), 'test.xml')
                return $doc)
            return <result>$doc/xml/root<tail foo="{$bar}" /></result>
        ''')

        results = await q1.updating()

        self.assertFalse(results)

        q2 = await self.session.query(b'''
            insert node (attribute { 'a' } { 5 }, 'text', <e/>) into /xml
        ''')

        results = await q2.updating()

        self.assertTrue(results)
