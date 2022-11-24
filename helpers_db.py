import sqlite3 as sql


def init_db_tables():
    conn = sql.connect("budget.db")

    query = """CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        year INTEGER NOT NULL,
        month quantity INTEGER NOT NULL,
        day INTEGER NOT NULL,
        description TEXT NOT NULL,
        tag TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        repeat INTEGER NOT NULL,
        fixed INTEGER
    )"""

    conn.execute(query)

    conn.close()


def insert_transaction(data):

    # data
    year = data["date"][0]
    month = data["date"][1]
    day = data["date"][2]
    description = data["description"]
    tag = data["tag"]
    amount = data["amount"]
    t_type = data["type"]
    fixed = data["fixed"]
    repeat = data["repeat"]

    try:
        with sql.connect("budget.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO transactions (year, month, day, description, tag, amount, type, repeat, fixed) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (year, month, day, description, tag, amount, t_type, repeat, fixed),
            )

            con.commit()
            msg = "success"
    except:
        con.rollback()
        msg = "error"
    finally:
        con.close()
        return msg


def select_month_data(year, month):

    con = sql.connect("budget.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute(
        "select * from transactions WHERE (year=? AND month=?) OR fixed=1",
        (year, month),
    )

    rows = cur.fetchall()

    return rows
