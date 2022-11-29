from cs50 import SQL
from flask import Flask, render_template, request, redirect
from helpers import get_date, get_month, get_prev_month, get_next_month
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
    date = get_date()
    return render_template("index.html", date=date)


# Add Transaction
@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        # Form data
        data = get_transaction_form_data()
        date = data['date']
        parcels = data['parcels']
        description = data['description']
        amount = data['amount']
        type = data['type']
        payed = data['payed']

        # TODO: handle invalid data

        # Variable to store current date for next parcel
        parcel_date = [date[0], date[1], date[2]]

        # Variable to store parcel id (id from first parcel)
        parcel_id = 0
            
        # insert each parcel
        for i in range(parcels):
            parcel = i + 1
            year = parcel_date[0]
            month = parcel_date[1]
            day = parcel_date[2]

            # if not first parcel => get next month
            if i > 0:
                d = get_next_month(parcel_date[0], parcel_date[1])
                year = d["year"]
                month = d["month"]
                payed = 0

                # update parcel current date
                parcel_date[0] = year
                parcel_date[1] = month

            # Insert transaction
            id = db.execute('''INSERT INTO transactions 
                               (year, month, day, description, amount, type, parcels, parcel, payed) 
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                year, month, day, description, amount, type, parcels, parcel, payed)

            # if first parcel => update parcel_id value
            if i == 0:
                parcel_id = id

            # update parcel id
            db.execute("UPDATE transactions SET parcel_id=? WHERE id=?", parcel_id, id)

        return redirect("/month/2022/11")
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

    if request.method == "POST":
        # Form data
        data = get_transaction_form_data()
        date = data['date']
        print(data)

        # If parcels count did not change
        if data['parcels'] == row[0]['parcels']:
            # Parcels = 1 => update single transaction
            db.execute("""UPDATE transactions
                          SET year=?, month=?, day=?, description=?, amount=?, type=?, payed=?
                          WHERE id=?""",
                          date[0], date[1], date[2], data['description'], data['amount'], data['type'], data['payed'], row[0]['id'])

            # Parcels > 1  and date didn't change => update all parcels
            db.execute("""UPDATE transactions
                          SET description=?, amount=?, type=?, payed=?
                          WHERE parcel_id=?""",
                          data['description'], data['amount'], data['type'], data['payed'], row[0]['parcel_id'])

            # Parcels > 1  and date changed => update all parcels dates
            new_date = data['date']
            for i in range(data['parcels']):
                parcel = i + 1
                db.execute("""UPDATE transactions
                              SET year=?, month=?, day=?
                              WHERE parcel_id=? AND parcel=?""",
                              new_date[0], new_date[1], new_date[2], row[0]['parcel_id'], parcel)

                # update new date
                new_month = get_next_month(new_date[0], new_date[1])
                new_date[0] = new_month['year']
                new_date[1] = new_month['month']

        else:
            # Transaction only had one parcel
            # Parcel count increased
            # parcel count decreased
            ...

        # TODO => get previous route
        return redirect("/month/2022/11") 
    else:
        # Data dict
        data = {
            "id": row[0]['id'],
            "date": f"{row[0]['year']}-{row[0]['month']}-{row[0]['day']}",
            "type": row[0]['type'],
            "amount": row[0]['amount'],
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
    total = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?)", year, month)
    out = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?) AND (type=?)", year, month, "out")
    income = db.execute("SELECT SUM(amount) from transactions WHERE (year=? AND month=?) AND (type=?)", year, month, "in")
    balance = {
        "total": total[0]['SUM(amount)'],
        "out": out[0]['SUM(amount)'],
        "income": income[0]['SUM(amount)']
    }

    # Add month transactions and balance to data dict
    data["rows"] = rows
    data["balance"] = balance

    # Get previous and next month from data => integers
    prev = get_prev_month(data['year'], data['month'])
    next = get_next_month(data['year'], data['month'])

    # TODO: handle error

    return render_template("month.html", data=data, prev=prev, next=next)


# Pending
@app.route("/pending")
def pending():
    return render_template("pending.html")


# Categories
@app.route("/categories/<year>/<month>")
def categories(year, month):
    data = get_month(year, month)
    return render_template("categories.html", data=data)


# Year
@app.route("/year/<year>")
def year(year):
    return render_template("year.html", year=year)


# Get add / edit form data
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
