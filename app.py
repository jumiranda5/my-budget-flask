from flask import Flask, render_template


app = Flask(__name__)


# Home
@app.route("/")
def index():
    return render_template("index.html")


# Month
@app.route("/month/<year>/<month>")
def month(year, month):
    return render_template("month.html")


# Pending
@app.route("/pending")
def pending():
    return render_template("pending.html")


# Categories
@app.route("/categories/<year>/<month>")
def categories(year, month):
    return render_template("categories.html")


# Year
@app.route("/year/<year>")
def year(year):
    return render_template("year.html")


# Add Transaction
@app.route("/add")
def add():
    return render_template("add.html")


# Edit Transaction
@app.route("/edit/<id>")
def edit(id):
    return render_template("edit.html")
