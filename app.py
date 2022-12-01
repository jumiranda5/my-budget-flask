from cs50 import SQL
from flask import Flask, render_template, request, redirect
from helpers import get_date, get_month, get_prev_month, get_next_month, get_year
from helpers import validate_date, validate_amount, validate_text, validate_repeat


app = Flask(__name__)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


# Create transactions table if it doesn't exist
db.execute('''CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    year INTEGER NOT NULL,
    month quantity INTEGER NOT NULL,
    day INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    parcels INTEGER DEFAULT 1,
    parcel INTEGER DEFAULT 1,
    parcel_id INTEGER,
    payed INTEGER DEFAULT 0)''')


# Home
@app.route("/")
def index():
    # Get today's date
    date = get_date()

    # Get month balance
    balance = get_month_balance(date['year'], date['month'])

    # Year
    year = get_year_balance(date["year"])
    
    # Get not payed transactions (pending) and sum
    not_payed = db.execute("""SELECT * FROM transactions 
                              WHERE year = ? AND month = ? AND day <= ?
                              OR (year <= ? AND month < ?) 
                              ORDER BY year, month, day""", 
        date["year"], date["month"], date["day"], date["year"], date["month"])

    pending_sum = db.execute("""SELECT SUM(amount) FROM transactions 
                                WHERE year = ? AND month = ? AND day <= ?
                                OR (year <= ? AND month < ?)""", 
        date["year"], date["month"], date["day"],date["year"], date["month"])

    pending_total = pending_sum[0]['SUM(amount)']

    # Return 0.0 if result is None
    if not pending_total:
        pending_total = 0.0

    # pending dict
    pending = {
        "rows": not_payed,
        "total": f"${pending_total:,.2f}"
    }

    return render_template("index.html", date=date, balance=balance, year=year, pending=pending)


# Add Transaction
@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        # Form data
        data = get_transaction_form_data()
        date = data['date']
        payed = data['payed']

        # TODO: handle invalid data

        # Variable to store current parcel
        parcel_date = [date[0], date[1], date[2]]
        parcel_id = 0
            
        # insert each parcel
        for i in range(data['parcels']):
            parcel = i + 1

            # if not first parcel => get next month
            if i > 0:
                d = get_next_month(parcel_date[0], parcel_date[1])
                parcel_date = [d["year"], d["month"], date[2]]
                payed = 0

            # Insert transaction
            id = insert_transaction(parcel_date[0], 
                                    parcel_date[1], 
                                    parcel_date[2], 
                                    data['description'], 
                                    data['amount'], 
                                    data['type'], 
                                    data['parcels'], 
                                    parcel, 
                                    None, 
                                    payed)

            # if first parcel => update parcel_id value
            if i == 0:
                parcel_id = id

            # update parcel_id
            db.execute("UPDATE transactions SET parcel_id=? WHERE id=?", parcel_id, id)

        return redirect(f"/month/{date[0]}/{date[1]}")
    else:
        today = get_date()
        today_formatted = f"{today['year']}-{today['month']}-{today['day']}"
        return render_template("add.html", today=today_formatted)


# Delete Transaction
@app.route("/delete/<year>/<month>/<id>/<parcels>", methods=["POST"])
def delete(year, month, id, parcels):
    # if transaction is repeated => delete by parcel_id
    if parcels == "1":
        db.execute("DELETE FROM transactions WHERE id=?", id)
    else:
        db.execute("DELETE FROM transactions WHERE parcel_id=?", id)

    # refresh page
    return redirect(f"/month/{year}/{month}")


# Edit Transaction
@app.route("/edit/<id>", methods=["POST", "GET"])
def edit(id):

    # Get transaction to edit
    row = db.execute("SELECT * FROM transactions WHERE id=?", id)
    date = f"{row[0]['year']}-{row[0]['month']:02d}-{row[0]['day']:02d}"

    # if transaction has parcels => get first parcel
    if row[0]['parcels'] > 1:
        first_parcel = db.execute("SELECT MIN(id) FROM transactions WHERE parcel_id=?", row[0]['parcel_id'])
        d = db.execute("SELECT year, month, day FROM transactions WHERE id=?", first_parcel[0]['MIN(id)'])
        date = f"{d[0]['year']}-{d[0]['month']:02d}-{d[0]['day']:02d}"

    if request.method == "POST":
        # Form data
        data = get_transaction_form_data()
        date = data['date']
        parcels = data['parcels']
        description = data['description']
        amount = data['amount']
        type = data['type']

        # Update transactions values
        if row[0]['parcels'] == 1:
            # If original parcel count is 1 => update all values
            update_single_transaction(date[0], date[1], date[2], description, amount, type, parcels, row[0]['id'])
        else:
            # Update all parcels
            original_date = [row[0]['year'], row[0]['month'], row[0]['day']]
            last_parcel_date = update_transaction_parcels(
                        original_date, 
                        date, 
                        description, 
                        amount, 
                        type, 
                        parcels, 
                        row[0]['parcel_id'])

        # If parcels count changed
        if not parcels == row[0]['parcels']:
            # Number of parcels to add/delete
            extra = parcels - row[0]['parcels']

            if extra > 0:
                # Parcel count increased => get last transaction date
                new_date = [last_parcel_date[0], last_parcel_date[1], date[2]]
                new_parcel = row[0]['parcels'] + 1

                for _ in range(extra):
                    # Insert transaction
                    insert_transaction(new_date[0], 
                                       new_date[1], 
                                       new_date[2], 
                                       description, 
                                       amount, 
                                       type, 
                                       parcels, 
                                       new_parcel, 
                                       row[0]['parcel_id'], 
                                       data['payed'])
                    
                    # Update new_date
                    new_month = get_next_month(new_date[0], new_date[1])
                    new_date[0] = new_month['year']
                    new_date[1] = new_month['month']

                    # Update new_parcel
                    new_parcel = new_parcel + 1
            else:
                # parcel count decreased => delete extra transactions
                # use abs() to get positive integer from negative extra
                for _ in range(abs(extra)):

                    # get last transaction id with parcel_id from row
                    last_id = db.execute("SELECT MAX(id) FROM transactions WHERE parcel_id=?", row[0]['parcel_id'])
                    id = last_id[0]['MAX(id)']

                    # Delete transaction
                    db.execute("DELETE FROM transactions WHERE id=?", id)

                    # update parcels count
                    db.execute("UPDATE transactions SET parcels=? WHERE parcel_id=?", parcels, row[0]['parcel_id'])

        return redirect(f"/month/{row[0]['year']}/{row[0]['month']}") 
    else:
        # Data dict
        data = {
            "id": row[0]['id'],
            "date": date,
            "type": row[0]['type'],
            "amount": abs(row[0]['amount']),
            "description": row[0]['description'],
            "payed": row[0]['payed'],
            "parcels": row[0]['parcels']
        }

        return render_template("edit.html", data=data)


# Edit Payed
@app.route('/edit-payed/<id>/<checked>', methods=["POST"])
def edit_payed(id, checked):
    # If checkbox is checked, toggle payed to 1 (payed)
    if checked == "true":
        payed = 1
    else:
        # toggle payed to 0 (not payed)
        payed = 0

    # update db
    db.execute("UPDATE transactions SET payed=? WHERE id=?", payed, id)

    return "success"


# Month
@app.route("/month/<year>/<month>")
def month(year, month):

    # Get month dict
    data = get_month(year, month)

    # Get month transactions from db
    rows = db.execute("SELECT * from transactions WHERE (year=? AND month=?)", year, month)

    # Get transactions balance
    balance = get_month_balance(year, month)

    # Add month transactions and balance to data dict
    data["rows"] = rows
    data["balance"] = balance

    # Get previous and next month from data => integers
    prev = get_prev_month(data['year'], data['month'])
    next = get_next_month(data['year'], data['month'])

    # TODO: handle error

    return render_template("month.html", data=data, prev=prev, next=next)


# -------------------------------------------------
#                     AJAX
# -------------------------------------------------

@app.route("/balance/<year>/<month>/<action>")
def month_balance(year, month, action):

    # Get month dict
    date = get_month(year, month)

    # Get previous or next
    if action == "prev":
        next = get_prev_month(date['year'], date['month'])
    else:
        next = get_next_month(date['year'], date['month'])

    # Get prev month dict
    date = get_month(next['year'], next['month'])

    # Get month balance
    balance = get_month_balance(next['year'], next['month'])

    print(balance)

    response = {
        "date": date,
        "balance": balance
    }

    return response


@app.route("/year-balance/<year>/<action>")
def year_balance(year, action):

    # Get date dict
    date = get_month(year, "1")

    # get next year
    if action == "prev":
        next_year = date['year'] - 1
    else:
        next_year = date['year'] + 1
    
    # return year object
    return get_year_balance(next_year)

# -------------------------------------------------
#                    REUSABLE
# -------------------------------------------------

def get_year_balance(year):
    
    year_months = get_year()
    year_balance = db.execute("SELECT SUM(amount) FROM transactions WHERE year = ?", year)
    year_balance = year_balance[0]['SUM(amount)']

    for row in year_months:
        row_balance = get_month_balance(year, row['month'])
        row['balance'] = row_balance

    return {
        "year": year,
        "months": year_months,
        "balance": year_balance
    }


def get_month_balance(year, month):
    # Get transactions balance
    total = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?)", year, month)
    out = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?) AND (type=?)", year, month, "out")
    income = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?) AND (type=?)", year, month, "in")

    total = total[0]['SUM(amount)']
    out = out[0]['SUM(amount)']
    income = income[0]['SUM(amount)']

    # Return 0.0 if result is None
    if not total:
        total = 0.0
    if not out:
        out = 0.0
    if not income:
        income = 0.0

    balance = {
        "total": f"${total:,.2f}",
        "out": f"${out:,.2f}",
        "income": f"${income:,.2f}"
    }

    return balance

def get_transaction_form_data():
    # Form data
    type = request.form["type"]
    date = validate_date(request.form["date"])
    description = validate_text(request.form["description"])
    parcels = validate_repeat(request.form["repeat"])

    # Make amount negative if expense
    if type == "out":
        amount = f"-{request.form['amount']}"
    else:
        amount = request.form["amount"]

    amount = validate_amount(amount)
    
    # payed checkbox
    if request.form.get("payed"):
        payed = 1
    else:
        payed = 0

    return {
        "type": type,
        "date": date,
        "description": description,
        "parcels": parcels,
        "amount": amount,
        "payed": payed
    }


# -------------------------------------------------
#                    DATABASE
# -------------------------------------------------

def insert_transaction(year, month, day, description, amount, type, parcels, parcel, parcel_id, payed):
    id = db.execute('''INSERT INTO transactions 
                               (year, month, day, description, amount, type, parcels, parcel, parcel_id, payed) 
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                year, month, day, description, amount, type, parcels, parcel, parcel_id, payed)
    return id


def update_single_transaction(year, month, day, description, amount, type, parcels, parcel_id):
    db.execute("""UPDATE transactions
                          SET year=?, month=?, day=?, description=?, amount=?, type=?, parcels=?
                          WHERE id=?""",
                          year, month, day, description, amount, type, parcels, parcel_id)


def update_transaction_parcels(date, new_date, description, amount, type, parcels, parcel_id):
    # Update without updating date
    db.execute("""UPDATE transactions
                    SET description=?, amount=?, type=?, parcels=?
                    WHERE parcel_id=?""",
                    description, amount, type, parcels, parcel_id)
    
    last_date = date

    if not date == new_date:
        # update all parcels dates
        parcels_rows = db.execute("SELECT * FROM transactions WHERE parcel_id=?", parcel_id)
        for parcel_row in parcels_rows:
            db.execute("""UPDATE transactions
                            SET year=?, month=?, day=?
                            WHERE id=? AND parcels=?""",
                            new_date[0], new_date[1], new_date[2], parcel_row['id'], parcels)

            # update last date
            last_date = new_date

            # update new date
            new_month = get_next_month(new_date[0], new_date[1])
            new_date[0] = new_month['year']
            new_date[1] = new_month['month']

    return last_date


