import psycopg2
from flask import g
import os

# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydatabase")

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db

def query_db(query, args=(), one=False):
    """
    Executes a query and returns the results.
    """
    con = get_db()
    con.row_factory = psycopg2.extras.RealDictCursor  # Enable dict results
    cur = con.cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    cur.close()

    # Return one result or the full result list
    return result[0] if one and result else result

def insert_db(query, args=()):
    """Inserts data into the database."""
    con = get_db()
    cur = con.cursor()
    cur.execute(query, args)
    con.commit()
    cur.close()

def close_connection(exception):
    """Closes the database connection when the application context ends."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
