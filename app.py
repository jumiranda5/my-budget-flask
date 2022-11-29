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


full_db = db.execute("SELECT * FROM transactions")
for row in full_db:
    print(f"{row['id']} | {row['year']} | {row['month']} | {row['day']} | {row['description']} | {row['amount']} | {row['parcels']} | {row['parcel']} | {row['parcel_id']}")


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
        parcels = data['parcels']
        description = data['description']
        amount = data['amount']
        type = data['type']

        # Variable to store last parcel date
        last_date = date

        # Update transactions values
        if row[0]['parcels'] == 1:
            # If original parcel count is 1 => update all values
            db.execute("""UPDATE transactions
                          SET year=?, month=?, day=?, description=?, amount=?, type=?, parcels=?
                          WHERE id=?""",
                          date[0], date[1], date[2], description, amount, type, parcels, row[0]['id'])
        else:
            # Update without updating date
            db.execute("""UPDATE transactions
                          SET description=?, amount=?, type=?, parcels=?
                          WHERE parcel_id=?""",
                          description, amount, type, parcels, row[0]['parcel_id'])
            
            # Parcels > 1  and date changed => update all parcels dates
            new_date = data['date']
            parcels_rows = db.execute("SELECT * FROM transactions WHERE parcel_id=?", row[0]['parcel_id'])
            for parcel_row in parcels_rows:
                db.execute("""UPDATE transactions
                              SET year=?, month=?, day=?
                              WHERE id=? AND parcels=?""",
                              new_date[0], new_date[1], new_date[2], parcel_row['id'], parcels)

                # update new date
                new_month = get_next_month(new_date[0], new_date[1])
                new_date[0] = new_month['year']
                new_date[1] = new_month['month']

                # update last date
                last_date = new_date

        # If parcels count changed
        if not parcels == row[0]['parcels']:
            # Number of parcels to add/delete
            extra = parcels - row[0]['parcels']
            print(f"===========> extra: {extra}")

            if extra > 0:
                # Parcel count increased => get last transaction date
                new_month = get_next_month(last_date[0], last_date[1])
                new_date = [new_month['year'], new_month['month'], date[2]]
                new_parcel = row[0]['parcels'] + 1

                for _ in range(extra):
                    # Insert transaction
                    db.execute('''INSERT INTO transactions 
                               (year, month, day, description, amount, type, parcels, parcel, parcel_id) 
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                new_date[0], new_date[1], new_date[2], description, amount, type, parcels, new_parcel, row[0]['parcel_id'])
                    
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
                    print(f'============> id: {id}')

                    # Delete transaction
                    db.execute("DELETE FROM transactions WHERE id=?", id)

                    # update parcels count
                    db.execute("UPDATE transactions SET parcels=? WHERE parcel_id=?", parcels, row[0]['parcel_id'])

        # TODO => get previous route
        return redirect("/month/2022/11") 
    else:
        # Data dict
        data = {
            "id": row[0]['id'],
            "date": f"{row[0]['year']}-{row[0]['month']:02d}-{row[0]['day']:02d}",
            "type": row[0]['type'],
            "amount": abs(row[0]['amount']),
            "description": row[0]['description'],
            "payed": row[0]['payed'],
            "parcels": row[0]['parcels']
        }

        print(f"===============> date: {data['date']}")

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
