import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_for_month(current):
    """
    Fetch the EB2 India date for a specific month (datetime object).
    Returns a dict with 'bulletin_date' and 'eb2_date', or None if not found.
    """
    month_name = calendar.month_name[current.month].lower()
    # Fiscal year logic for URL path
    if current.month >= 10:  # October, November, December
        url_year = current.year + 1
    else:
        url_year = current.year
    url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{url_year}/visa-bulletin-for-{month_name}-{current.year}.html"
    print(f"Fetching: {url}")
    try:
        resp = requests.get(url, timeout=10, verify=False)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if not rows or len(rows) < 2:
                continue
            header_cells = [th.get_text(strip=True).lower() for th in rows[0].find_all(["td", "th"])]
            if not any("india" in h for h in header_cells):
                continue
            try:
                india_idx = header_cells.index(next(h for h in header_cells if "india" in h))
            except StopIteration:
                continue
            for row in rows[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) <= india_idx:
                    continue
                if "2nd" in cells[0].lower() or "eb2" in cells[0].lower():
                    eb2_date = cells[india_idx]
                    return {
                        "bulletin_date": current.strftime("%B %Y"),
                        "eb2_date": eb2_date
                    }
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_bulletin_date(b):
    """
    Parse a dict with a 'bulletin_date' key into a datetime object.
    """
    return datetime.strptime(b["bulletin_date"], "%B %Y")

def fetch_eb2_india_dates(start_month, start_year, end_month, end_year):
    """
    Scrape the US Visa Bulletin for EB2 India dates between the given start and end month/year.
    Returns a list of dicts with 'bulletin_date' and 'eb2_date'.
    """
    results = []
    start_date = datetime(int(start_year), int(start_month), 1)
    end_date = datetime(int(end_year), int(end_month), 1)
    # Prepare all months
    months = []
    current = start_date
    while current <= end_date:
        months.append(current)
        current = add_months(current, 1)
    # Fetch in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_month = {executor.submit(fetch_for_month, month): month for month in months}
        month_results = []
        for future in as_completed(future_to_month):
            result = future.result()
            if result:
                month_results.append(result)
    # Sort results by bulletin_date (chronologically)
    results = sorted(month_results, key=parse_bulletin_date)
    print("Scraped Results:", results)
    return results

def add_months(date_obj, months):
    """
    Add a number of months to a datetime object, returning a new datetime at the first of the resulting month.
    """
    year = date_obj.year + (date_obj.month + months - 1) // 12
    month = (date_obj.month + months - 1) % 12 + 1
    return datetime(year, month, 1)

__all__ = ["fetch_eb2_india_dates", "add_months", "fetch_for_month", "parse_bulletin_date"] 