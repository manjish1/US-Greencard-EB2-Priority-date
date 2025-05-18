from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

def fetch_eb2_india_dates(start_month, start_year, end_month, end_year):
    results = []
    start_date = datetime(int(start_year), int(start_month), 1)
    end_date = datetime(int(end_year), int(end_month), 1)

    def fetch_for_month(current):
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
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    if len(cells) < 4:
                        continue
                    if "2nd" in cells[0].lower() or "eb2" in cells[0].lower():
                        eb2_date = cells[3]
                        return {
                            "bulletin_date": current.strftime("%B %Y"),
                            "eb2_date": eb2_date
                        }
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

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
    def parse_bulletin_date(b):
        return datetime.strptime(b["bulletin_date"], "%B %Y")
    results = sorted(month_results, key=parse_bulletin_date)
    print("Scraped Results:", results)
    return results

def add_months(date_obj, months):
    year = date_obj.year + (date_obj.month + months - 1) // 12
    month = (date_obj.month + months - 1) % 12 + 1
    return datetime(year, month, 1)

@app.route("/", methods=["GET"])
def index():
    results = []
    start_month = request.args.get("start_month")
    start_year = request.args.get("start_year")
    end_month = request.args.get("end_month")
    end_year = request.args.get("end_year")
    if start_month and start_year and end_month and end_year:
        results = fetch_eb2_india_dates(start_month, start_year, end_month, end_year)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
