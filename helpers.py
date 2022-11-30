from datetime import datetime
from calendar import month_name, month_abbr
import re


def get_date():
    # Get current date
    today = datetime.now()

    # Date dictionary
    date = {
        "year": today.year,
        "month": today.month,
        "month_name": month_name[today.month],
        "day": today.day,
    }

    return date


def get_month(year, month):
    # Validate year and month and convert to integers
    valid = validate_date(f"{year}-{month}-01")
    if not valid == "invalid":
        year = int(year)
        month = int(month)
    else:
        return "invalid month"

    # return month dictionary
    return {"year": year, "month": month, "month_name": month_name[month]}


def get_next_month(year, month):
    # return error msg if month and year are not integers
    if not isinstance(year, int) or not isinstance(month, int):
        return "invalid format"

    # if month is december, start new year
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    return {"year": next_year, "month": next_month}


def get_prev_month(year, month):
    # return error msg if month and year are not integers
    if not isinstance(year, int) or not isinstance(month, int):
        return "invalid format"

    # if january, start previous year on december
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    return {"year": prev_year, "month": prev_month}


def get_year():

    year = []

    for i in range(12):
        m = i + 1
        # Date dictionary
        month = {
            "month": m,
            "month_name": month_name[m],
        }

        year.append(month)

    return year



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
        return "invalid"

    # return list of integers
    return [year, month, day]


def validate_amount(amount):
    # If amount in null => amount = 0
    if not amount:
        amount = "0.0"

    # get float from amount
    amount = re.sub(r"[^0-9.,-]", "", amount)
    amount = amount.replace(",", ".")
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
        return "invalid"
