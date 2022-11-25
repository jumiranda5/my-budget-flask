from datetime import datetime
from calendar import month_name
from helpers_db import select_month_data
import re


def get_date():
    # Get current date
    today = datetime.now()

    # Date dictionary
    date = {
        "year": today.year,
        "month": today.month,
        "month_name": month_name[today.month],
        "day": today.day 
    }

    return date


def get_month_data(year, month):

    # Validate month as an integer from 1 to 12
    try:
        month = int(month)
        year = int(year)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return "Invalid month"

    # Get data from db
    rows = select_month_data(year, month)

    # return month dictionary
    return {
        "year": year,
        "month": month,
        "month_name": month_name[month],
        "rows": rows
    }


def validate_date(date):
    # Return invalid if date is empty
    if not date:
        return "invalid"

    # Date format must be yyyy-mm-dd
    d = date.split("-")

    try:
        year = int(d[0])
        month = int(d[1])
        day = int(d[2])

        # month and day must not be more than 12/31 and year length must be 4 
        if month > 12 or day > 31 or not len(str(year)) == 4:
            raise ValueError

        # year, month and day must be positive
        if month <= 0 or day <= 0 or year <= 0:
            raise ValueError

    except ValueError:
        return 'invalid'

    # return list of integers
    return [year, month, day]


def validate_amount(amount):
    # If amount in null => amount = 0
    if not amount:
        amount = "0.0"

    # get float from amount
    amount = re.sub(r"[^0-9.,]", "", amount)
    amount = amount.replace("," , ".")
    parts = amount.split(".")
    if len(parts) > 1:
        decimals = parts[-1]
        parts.pop()
        amount = f"{''.join(parts)}.{decimals}"
    else:
        amount = parts[0]

    # Amount should be a float or an integer that converts to float
    try:
        a = float(amount)
    except ValueError:
        return "invalid"
    
    # return float
    return a


def validate_text(text):
    # if text is empty, return empty str
    if not text:
        return ""

    # remove some untrusted characters
    t = re.sub(r"[<>=&|;$`!+=\\]", "", text)
    return t


def validate_repeat(repeat):
    # if repeat is empty => return None
    if not repeat:
        return 1

    # Must be a positive integer
    try:
        r = int(repeat)
        if r <= 0:
            return 1
        return r
    except:
        return 'invalid'
