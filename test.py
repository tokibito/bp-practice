# coding: utf-8
import unittest
from unittest import TestCase
from datetime import datetime
from playhouse.test_utils import test_database
from guestbook import Greeting
from peewee import SqliteDatabase
import bottle
from StringIO import StringIO

test_db = SqliteDatabase(':memory:')

class SaveDataTest(TestCase):
    def getOne(self):
        from guestbook import save_data
        return save_data

    def test_save_success(self):
        """投稿データがデータベースに正常に保存されること
        """
        save_data = self.getOne()
        with test_database(test_db, (Greeting,)):
            save_data(u'tokibito', u'テスト', datetime(2013, 12, 2, 10, 0))
            greeting_list = list(Greeting.select())
            self.assertEqual(len(greeting_list), 1)
            self.assertEqual(greeting_list[0].name, u'tokibito')
            self.assertEqual(greeting_list[0].comment, u'テスト')
            self.assertEqual(greeting_list[0].create_at, datetime(2013, 12, 2, 10, 0))


class LoadDataEmptyTest(TestCase):
    """load_data関数のテスト
    データが空の場合
    """
    def getOne(self):
        from guestbook import load_data
        return load_data

    def test_load_success(self):
        """呼び出しが正常に完了して、結果が空になること
        """
        with test_database(test_db, (Greeting,)):
            load_data = self.getOne()
            greeting_list = list(load_data())
            self.assertEqual(greeting_list, [])


class LoadDataExistTest(TestCase):
    """load_data関数のテスト
    データが存在する場合
    """
    def getOne(self):
        from guestbook import load_data
        return load_data

    def setUp(self):
        self.db = test_database(test_db, (Greeting,))
        self.db.__enter__()
        # データを2件作成
        Greeting.create(
            name=u'tokibito',
            comment=u'テスト',
            create_at=datetime(2013, 12, 3, 10, 0))
        Greeting.create(
            name=u'spam',
            comment=u'egg',
            create_at=datetime(2013, 12, 4, 11, 0))

    def tearDown(self):
        self.db.__exit__(None, None, None)

    def test_load_success(self):
        """呼び出しが正常に完了して、結果が2件になること
        """
        load_data = self.getOne()
        greeting_list = list(load_data())
        self.assertEqual(len(greeting_list), 2)

    def test_descending(self):
        """呼び出しが正常に完了して、作成日時の降順になること
        """
        load_data = self.getOne()
        greeting_list = list(load_data())
        self.assertEqual([g.name for g in greeting_list], [u'spam', u'tokibito'])


class IndexTest(TestCase):
    """トップページのテスト
    """
    def getOne(self):
        from guestbook import index
        return index

    def test_rendering(self):
        """レンダリングが正常に完了していること
        """
        index = self.getOne()
        with test_database(test_db, (Greeting,)):
            html = index()
        self.assertTrue(len(html) > 0)


class IndexDataExistTest(TestCase):
    """トップページのテスト(データが存在する場合)
    """
    def getOne(self):
        from guestbook import index
        return index

    def setUp(self):
        self.db = test_database(test_db, (Greeting,))
        self.db.__enter__()
        # データを2件作成
        Greeting.create(
            name=u'tokibito',
            comment=u'テスト',
            create_at=datetime(2013, 12, 3, 10, 0))
        Greeting.create(
            name=u'spam',
            comment=u'egg',
            create_at=datetime(2013, 12, 4, 11, 0))

    def tearDown(self):
        self.db.__exit__(None, None, None)

    def test_rendering(self):
        """レンダリングが正常に完了していること
        """
        index = self.getOne()
        html = index()
        self.assertTrue(len(html) > 0)
        self.assertIn("tokibito", html)


class PostTest(TestCase):
    """投稿のテスト
    """
    def getOne(self):
        from guestbook import post
        return post

    def setUp(self):
        self.db = test_database(test_db, (Greeting,))
        self.db.__enter__()

    def tearDown(self):
        self.db.__exit__(None, None, None)

    def test_success(self):
        bottle.request = bottle.LocalRequest(
            {'wsgi.input': StringIO('name=tokibito&comment=テスト'),
             'CONTENT_LENGTH': 31})
        post = self.getOne()
        try:
            post()
        except bottle.HTTPResponse as res:
            self.assertEqual(res.headers['Location'], 'http://127.0.0.1/')
        greeting_list = list(Greeting.select())
        self.assertEqual(len(greeting_list), 1)
        self.assertEqual(greeting_list[0].name, 'tokibito')
        self.assertEqual(greeting_list[0].comment, u'テスト')


class NL2BRTest(TestCase):
    """nl2br関数のテスト
    """
    def getOne(self):
        from guestbook import nl2br
        return nl2br

    def test_include_newline(self):
        """改行を含む場合
        """
        nl2br = self.getOne()
        self.assertEqual(nl2br('a\nb\nc'), 'a<br />b<br />c')

    def test_nothing_newline(self):
        """改行を含まない
        """
        nl2br = self.getOne()
        self.assertEqual(nl2br('abc'), 'abc')


class DatetimeFmtTest(TestCase):
    """datetime_fmt関数のテスト
    """
    def getOne(self):
        from guestbook import datetime_fmt
        return datetime_fmt

    def test_success(self):
        """datetimeオブジェクトを正常に文字列に変換できること
        """
        datetime_fmt = self.getOne()
        self.assertEqual(
            datetime_fmt(datetime(2013, 12, 6, 14, 15, 30)),
            '2013/12/06 14:15:30')


if __name__ == '__main__':
    unittest.main()
