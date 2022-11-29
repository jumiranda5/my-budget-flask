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

        # TODO: handle invalid data

        if parcels > 1:
            # get last row id and increment to add as parcel_id
            last_id = db.execute("SELECT MAX(id) FROM transactions")
            parcel_id = last_id[0]['MAX(id)'] + 1
        else:
            parcel_id = None

        # Variable to store current date for next parcel
        parcel_date = [date[0], date[1], date[2]]
            
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
            db.execute('''INSERT INTO transactions 
                        (year, month, day, description, amount, type, parcels, parcel, parcel_id, payed) 
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        year, month, day, description, amount, type, parcels, parcel, parcel_id, payed)

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
@app.route("/edit/<id>")
def edit(id):
    return render_template("edit.html")


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

    # Add month transactions to data dict
    data["rows"] = rows

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
