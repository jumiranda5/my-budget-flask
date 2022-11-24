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


def test_validate_date():
    assert h.validate_date("22-11-24") == "invalid"
    assert h.validate_date("24-11-2022") == "invalid"
    assert h.validate_date("aa-aa-aaaa") == "invalid"
    assert h.validate_date("00-00-0000") == "invalid"
    assert h.validate_date("24-11-2022") == "invalid"
    assert h.validate_date("32-11-2022") == "invalid"
    assert h.validate_date(None) == "invalid"
    assert h.validate_date("2022-11-24") == [2022, 11, 24]


def test_validate_amount():
    assert h.validate_amount(None) == 0.0
    assert h.validate_amount("abc") == "invalid"
    assert h.validate_amount("$10,000.00") == 10000.0
    assert h.validate_amount("10.000,00") == 10000.0
    assert h.validate_amount("$10,000.00%!") == 10000.0


def test_validate_text():
    assert h.validate_text(None) == ""
    assert h.validate_text("<script>danger<script>") == "scriptdangerscript"
    assert h.validate_text("105 OR 1=1") == "105 OR 11"
    assert h.validate_text("valid text") == "valid text"
    assert h.validate_text("John's") == "John's"


def test_validate_repeat():
    assert h.validate_repeat("") == 1
    assert h.validate_repeat(None) == 1
    assert h.validate_repeat("0") == 1
    assert h.validate_repeat("-1") == 1
    assert h.validate_repeat("abc") == "invalid"
    assert h.validate_repeat("2") == 2