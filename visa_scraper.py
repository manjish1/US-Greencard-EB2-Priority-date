import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import json
import os

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
        resp = requests.get(url, timeout=10)
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch EB2 India dates and output as JSON.")
    parser.add_argument('--start-month', type=int, default=1, help='Start month (1-12)')
    parser.add_argument('--start-year', type=int, default=2014, help='Start year (e.g., 2014)')
    parser.add_argument('--end-month', type=int, default=datetime.now().month, help='End month (1-12)')
    parser.add_argument('--end-year', type=int, default=datetime.now().year, help='End year (e.g., 2024)')
    parser.add_argument('--output', type=str, default=None, help='Output file (default: stdout)')
    args = parser.parse_args()

    results = fetch_eb2_india_dates(args.start_month, args.start_year, args.end_month, args.end_year)
    # Pre-process: parse all dates to ISO format for easy loading
    for r in results:
        dt = None
        try:
            dt = datetime.strptime(r['eb2_date'], '%d%b%Y')
        except Exception:
            try:
                dt = datetime.strptime(r['eb2_date'], '%d%b%y')
            except Exception:
                dt = None
        r['eb2_date_iso'] = dt.strftime('%Y-%m-%d') if dt else None
    if args.output:
        if os.path.isdir(args.output):
            # Write each month as a separate file
            for r in results:
                # Parse bulletin_date to YYYY-MM
                try:
                    dt = datetime.strptime(r['bulletin_date'], '%B %Y')
                    fname = f"{dt.year:04d}-{dt.month:02d}.json"
                    with open(os.path.join(args.output, fname), 'w') as f:
                        json.dump(r, f, indent=2)
                except Exception as e:
                    print(f"Error writing month file: {e}")
        else:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
    else:
        json.dump(results, sys.stdout, indent=2)

__all__ = ["fetch_eb2_india_dates", "add_months", "fetch_for_month", "parse_bulletin_date"] 