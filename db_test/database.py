import sqlite3
from flask import g

DATABASE = 'database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    result = [dict(row) for row in rv]

    return result[0] if one and result else result


def insert_db(query, args=()):
    con = get_db()
    cur = con.execute(query, args)
    con.commit()
    cur.close()


# @app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
