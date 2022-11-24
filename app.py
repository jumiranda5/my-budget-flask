from flask import Flask, render_template, request, redirect
from helpers import get_date, get_month_data
from helpers import validate_date, validate_amount, validate_text, validate_repeat
from helpers_db import init_db_tables


app = Flask(__name__)


# Create database tables if they don't exist
init_db_tables()


# Home
@app.route("/")
def index():
    date = get_date()
    return render_template("index.html", date=date)


# Month
@app.route("/month/<year>/<month>")
def month(year, month):
    data = get_month_data(year, month)
    return render_template("month.html", data=data)


# Pending
@app.route("/pending")
def pending():
    return render_template("pending.html")


# Categories
@app.route("/categories/<year>/<month>")
def categories(year, month):
    data = get_month_data(year, month)
    return render_template("categories.html", data=data)


# Year
@app.route("/year/<year>")
def year(year):
    return render_template("year.html", year=year)


# Add Transaction
@app.route("/add", methods = ['POST', 'GET'])
def add():
    if request.method == "POST":
        # Form checkbox
        if request.form.get('fixed'):
            fixed = 1
        else:
            fixed = 0

        # Create dictionary with validated inputs
        data = {
            "date": validate_date(request.form['date']),
            "amount": validate_amount(request.form['amount']),
            "description": validate_text(request.form['description']),
            "tag": validate_text(request.form['tag']),
            "fixed": fixed,
            "repeat": validate_repeat(request.form['repeat'])
        }

        # Insert data on db
        print(f"==================> {data['date']}")
        print(f"==================> {data['amount']}")
        print(f"==================> {data['description']}")
        print(f"==================> {data['tag']}")
        print(f"==================> {data['fixed']}")
        print(f"==================> {data['repeat']}")

        return redirect("/month/2022/11")
    else:
        today = get_date()
        today_formatted = f"{today['year']}-{today['month']}-{today['day']}"
        return render_template("add.html", today=today_formatted)


# Edit Transaction
@app.route("/edit/<id>")
def edit(id):
    return render_template("edit.html")
