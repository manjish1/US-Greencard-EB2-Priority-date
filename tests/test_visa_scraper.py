import pytest
from datetime import datetime
from visa_scraper import add_months, parse_bulletin_date, fetch_for_month, fetch_eb2_india_dates
import requests
import requests_mock

# Test add_months
@pytest.mark.parametrize("start, months, expected", [
    (datetime(2020, 1, 1), 1, datetime(2020, 2, 1)),
    (datetime(2020, 1, 1), 12, datetime(2021, 1, 1)),
    (datetime(2020, 12, 1), 1, datetime(2021, 1, 1)),
    (datetime(2020, 6, 1), 7, datetime(2021, 1, 1)),
    (datetime(2020, 11, 1), 2, datetime(2021, 1, 1)),
])
def test_add_months(start, months, expected):
    assert add_months(start, months) == expected

def test_parse_bulletin_date():
    d = {"bulletin_date": "January 2020"}
    assert parse_bulletin_date(d) == datetime(2020, 1, 1)

# Mock HTML for fetch_for_month and fetch_eb2_india_dates
def visa_bulletin_html(eb2_date="01JAN20"):
    return f"""
    <html><body>
    <table>
        <tr><th>Preference</th><th>All Chargeability</th><th>China</th><th>India</th></tr>
        <tr><td>2nd</td><td>C</td><td>01JAN20</td><td>{eb2_date}</td></tr>
    </table>
    </body></html>
    """

def test_fetch_for_month_success(requests_mock):
    # Patch the URL pattern
    dt = datetime(2020, 1, 1)
    url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2020/visa-bulletin-for-january-2020.html"
    requests_mock.get(url, text=visa_bulletin_html("15JAN20"))
    result = fetch_for_month(dt)
    assert result["bulletin_date"] == "January 2020"
    assert result["eb2_date"] == "15JAN20"

def test_fetch_for_month_no_table(requests_mock):
    dt = datetime(2020, 1, 1)
    url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2020/visa-bulletin-for-january-2020.html"
    requests_mock.get(url, text="<html><body>No table here</body></html>")
    assert fetch_for_month(dt) is None

def test_fetch_for_month_http_error(requests_mock):
    dt = datetime(2020, 1, 1)
    url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2020/visa-bulletin-for-january-2020.html"
    requests_mock.get(url, status_code=404)
    assert fetch_for_month(dt) is None

def test_fetch_eb2_india_dates_parallel(monkeypatch):
    # Patch fetch_for_month to return predictable results
    from visa_scraper import fetch_eb2_india_dates
    def fake_fetch_for_month(dt):
        return {"bulletin_date": dt.strftime("%B %Y"), "eb2_date": "FAKE"}
    monkeypatch.setattr("visa_scraper.fetch_for_month", fake_fetch_for_month)
    results = fetch_eb2_india_dates(1, 2020, 3, 2020)
    assert len(results) == 3
    assert results[0]["bulletin_date"] == "January 2020"
    assert results[1]["bulletin_date"] == "February 2020"
    assert results[2]["bulletin_date"] == "March 2020"
    for r in results:
        assert r["eb2_date"] == "FAKE" 