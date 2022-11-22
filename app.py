from flask import Flask, render_template
from helpers import get_date, get_month_data


app = Flask(__name__)


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
@app.route("/add")
def add():
    return render_template("add.html")


# Edit Transaction
@app.route("/edit/<id>")
def edit(id):
    return render_template("edit.html")
