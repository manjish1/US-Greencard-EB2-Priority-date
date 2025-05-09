from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import calendar

app = Flask(__name__)

def fetch_eb2_india_dates(start_month, start_year, end_month, end_year):
    results = []
    start_date = datetime(int(start_year), int(start_month), 1)
    end_date = datetime(int(end_year), int(end_month), 1)

    current = start_date
    while current <= end_date:
        month_name = calendar.month_name[current.month].lower()
        url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{current.year}/visa-bulletin-for-{month_name}-{current.year}.html"
        print(f"Fetching: {url}")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                current = add_months(current, 1)
                continue
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
                        results.append({
                            "bulletin_date": current.strftime("%B %Y"),
                            "eb2_date": eb2_date
                        })
                        break
                if results and results[-1]["bulletin_date"] == current.strftime("%B %Y"):
                    break
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        current = add_months(current, 1)

    print("Scraped Results:", results)
    return results

def add_months(date_obj, months):
    year = date_obj.year + (date_obj.month + months - 1) // 12
    month = (date_obj.month + months - 1) % 12 + 1
    return datetime(year, month, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        start_month = request.form.get("start_month")
        start_year = request.form.get("start_year")
        end_month = request.form.get("end_month")
        end_year = request.form.get("end_year")
        results = fetch_eb2_india_dates(start_month, start_year, end_month, end_year)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
