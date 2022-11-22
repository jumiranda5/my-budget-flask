import helpers as h
from datetime import datetime
from calendar import month_name


def test_get_date():
    today = datetime.now()
    assert h.get_date()["year"] == today.year
    assert h.get_date()["month"] == today.month
    assert h.get_date()["month_name"] == month_name[today.month]
    assert h.get_date()["day"] == today.day
    assert h.get_date() == {
            "year": today.year, 
            "month": today.month, 
            "month_name": month_name[today.month],
            "day": today.day
        }


def test_get_month_data():
    assert h.get_month_data("2022", "abc") == "Invalid month"
    assert h.get_month_data("2022", "0") == "Invalid month"
    assert h.get_month_data("2022", "13") == "Invalid month"
    assert h.get_month_data("2022", "11") == {
            "year": 2022, 
            "month": 11, 
            "month_name": month_name[11]
        }