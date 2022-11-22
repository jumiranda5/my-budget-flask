import sqlite3 as sql

def init_db_tables():
    conn = sql.connect('budget.db')

    query = '''CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        year INTEGER NOT NULL,
        month quantity INTEGER NOT NULL,
        day INTEGER NOT NULL,
        description TEXT NOT NULL,
        tag TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        repeat INTEGER NOT NULL,
        permanent INTEGER
    )'''

    conn.execute(query)

    conn.close()