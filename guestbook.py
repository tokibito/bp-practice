# coding: utf-8
import os
from datetime import datetime

import peewee
from bottle import route, get, post, request, run
from bottle import template, static_file, redirect, html_escape

from jinja2 import Environment, FileSystemLoader, escape, Markup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'guestbook.dat')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
db = peewee.SqliteDatabase(DATA_FILE)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class Greeting(peewee.Model):
    """投稿データのモデル
    """
    name = peewee.CharField()
    comment = peewee.TextField()
    create_at = peewee.DateTimeField()

    class Meta:
        database = db


def create_table():
    """データベースファイルがなければデータベーステーブルを作成します
    """
    if not os.path.exists(DATA_FILE):
        Greeting.create_table()


def save_data(name, comment, create_at):
    """投稿データを保存します
    """
    Greeting.create(name=name, comment=comment, create_at=create_at)


def load_data():
    """投稿されたデータを返します
    """
    greeting_list = Greeting.select().order_by(Greeting.create_at.desc())
    return greeting_list


@get('/')
def index():
    """トップページ
    テンプレートを使用してページを表示します
    """
    greeting_list = load_data()
    template = env.get_template('index.html')
    return template.render(greeting_list=greeting_list)

@post('/post')
def post():
    """投稿用URL
    """
    name = request.forms.name
    comment = request.forms.comment
    create_at = datetime.now()
    # データを保存します
    save_data(name, comment, create_at)
    return redirect('/')


@route('/static/<filename:path>')
def send_static(filename):
    """静的ファイルを返します
    """
    return static_file(filename, root=STATIC_DIR)


def nl2br(s):
    """改行文字をbrタグに置き換える関数
    """
    return escape(s).replace('\n', Markup('<br />'))

env.filters['nl2br'] = nl2br


def datetime_fmt(dt):
    """datetimeオブジェクトを見やすい表示にする関数
    """
    return dt.strftime('%Y/%m/%d %H:%M:%S')

env.filters['datetime_fmt'] = datetime_fmt


if __name__ == '__main__':
    create_table()
    run(host='0.0.0.0', port=5000)
