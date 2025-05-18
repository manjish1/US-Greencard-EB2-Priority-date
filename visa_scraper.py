import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import json
import os
import time

def fetch_for_month(current, max_retries=3, backoff_factor=2):
    """
    Fetch the EB2 India date for a specific month (datetime object).
    Returns a dict with 'bulletin_date' and 'eb2_date', or None if not found.
    Retries on failure up to max_retries times with exponential backoff.
    If a 404 is encountered, tries the alternate URL format (with or without '-for').
    If the page is fetched but no India column is found, returns a result with eb2_date=None and a note.
    Handles old bulletins where the header may be 'IN' instead of 'India'.
    """
    month_name = calendar.month_name[current.month].lower()
    # Fiscal year logic for URL path
    if current.month >= 10:  # October, November, December
        url_year = current.year + 1
    else:
        url_year = current.year
    # Two possible URL formats
    url_with_for = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{url_year}/visa-bulletin-for-{month_name}-{current.year}.html"
    url_without_for = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{url_year}/visa-bulletin-{month_name}-{current.year}.html"
    urls_to_try = [url_with_for, url_without_for]
    attempt = 0
    tried_alternate = False
    while attempt < max_retries:
        for url in urls_to_try:
            print(f"Fetching: {url}")
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 404 and not tried_alternate:
                    # Try the alternate format if not already tried
                    print(f"404 Not Found for {url}. Trying alternate URL format.")
                    tried_alternate = True
                    continue
                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}")
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                found_india = False
                for table in tables:
                    rows = table.find_all("tr")
                    if not rows or len(rows) < 2:
                        continue
                    header_cells = [th.get_text(strip=True).lower() for th in rows[0].find_all(["td", "th"])]
                    # Find index for 'india' or 'in' (case-insensitive)
                    india_indices = [i for i, h in enumerate(header_cells) if ("india" in h or h.strip() == "in")]
                    if not india_indices:
                        continue
                    found_india = True
                    india_idx = india_indices[0]
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
                # If we parsed tables but found no India column, return a result with note
                if tables and not found_india:
                    return {
                        "bulletin_date": current.strftime("%B %Y"),
                        "eb2_date": None,
                        "note": "No India column"
                    }
                # If no tables at all, treat as not found (could be a malformed or irrelevant page)
                return None
            except Exception as e:
                attempt += 1
                print(f"Error fetching {url} (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    sleep_time = backoff_factor ** (attempt - 1)
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"Failed to fetch {url} after {max_retries} attempts.")
                    return None
        # After trying both formats, break if alternate was already tried
        if tried_alternate:
            break

def parse_bulletin_date(b):
    """
    Parse a dict with a 'bulletin_date' key into a datetime object.
    """
    return datetime.strptime(b["bulletin_date"], "%B %Y")

def fetch_eb2_india_dates(start_month, start_year, end_month, end_year, output_dir=None):
    """
    Scrape the US Visa Bulletin for EB2 India dates between the given start and end month/year.
    Returns a list of dicts with 'bulletin_date' and 'eb2_date'.
    If output_dir is provided and is a directory, skips months that already have a cache file.
    """
    results = []
    start_date = datetime(int(start_year), int(start_month), 1)
    end_date = datetime(int(end_year), int(end_month), 1)
    # Prepare all months
    months = []
    current = start_date
    while current <= end_date:
        # If output_dir is set, skip if file exists
        if output_dir and os.path.isdir(output_dir):
            fname = f"{current.year:04d}-{current.month:02d}.json"
            out_path = os.path.join(output_dir, fname)
            if os.path.exists(out_path):
                print(f"Skipping fetch for {fname}: already exists.")
                current = add_months(current, 1)
                continue
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

    results = fetch_eb2_india_dates(args.start_month, args.start_year, args.end_month, args.end_year, output_dir=args.output if args.output and os.path.isdir(args.output) else None)
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
                    out_path = os.path.join(args.output, fname)
                    if os.path.exists(out_path):
                        print(f"Skipping {fname}: already exists.")
                        continue
                    with open(out_path, 'w') as f:
                        json.dump(r, f, indent=2)
                except Exception as e:
                    print(f"Error writing month file: {e}")
        else:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
    else:
        json.dump(results, sys.stdout, indent=2)

__all__ = ["fetch_eb2_india_dates", "add_months", "fetch_for_month", "parse_bulletin_date"] 