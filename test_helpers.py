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
        "day": today.day,
    }


def test_get_month():
    assert h.get_month("2022", "abc") == "invalid month"
    assert h.get_month("2022", "0") == "invalid month"
    assert h.get_month("2022", "13") == "invalid month"
    assert h.get_month("2022", "11") == {
        "year": 2022,
        "month": 11,
        "month_name": month_name[11],
    }


def test_get_next_month():
    assert h.get_next_month(2022, 11) == {"year": 2022, "month": 12}
    assert h.get_next_month(2022, 12) == {"year": 2023, "month": 1}
    assert h.get_next_month("2022", "12") == "invalid format"


def test_get_prev_month():
    assert h.get_prev_month(2022, 1) == {"year": 2021, "month": 12}
    assert h.get_prev_month(2022, 11) == {"year": 2022, "month": 10}
    assert h.get_next_month("2022", "12") == "invalid format"


def test_get_year():
    assert h.get_year()[0] == {'month': 1, 'month_name': 'January'}
    assert h.get_year()[11] == {'month': 12, 'month_name': 'December'}


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
    assert h.validate_amount("100") == 100.0
    assert h.validate_amount("-100") == -100.0


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
