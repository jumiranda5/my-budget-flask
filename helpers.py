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

    return {
        "year": year,
        "month": month,
        "month_name": month_name[int(month)]
    }