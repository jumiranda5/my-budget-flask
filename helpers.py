from datetime import datetime
from calendar import month_name

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
        m = int(month)
        y = int(year)
        if m < 1 or m > 12:
            raise ValueError
    except ValueError:
        return "Invalid month"

    # return month dictionary
    return {
        "year": y,
        "month": m,
        "month_name": month_name[m]
    }