from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import calendar

app = Flask(__name__)

def fetch_visa_bulletin_dates(start_date, end_date):
    results = []

    current = start_date
    while current <= end_date:
        url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{current.year}/visa-bulletin-for-{calendar.month_name[current.month].lower()}-{current.year}.html"
        print(f"Fetching: {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            current = add_months(current, 1)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")

        found = False
        for table in tables:
            if "Employment" in table.text or "Employment-based" in table.text:
                df = pd.read_html(str(table))[0]
                for idx, row in df.iterrows():
                    if "India" in str(row).lower() and "eb2" in str(row).lower():
                        try:
                            eb2_date = row[["India", "2nd"]].dropna().values[0]
                        except:
                            continue
                        results.append({
                            "Visa Bulletin Date": current.strftime("%B %Y"),
                            "EB2 India Priority Date": eb2_date
                        })
                        found = True
                        break
            if found:
                break
        current = add_months(current, 1)

    return results

def add_months(date_obj, months):
    year = date_obj.year + (date_obj.month + months - 1) // 12
    month = (date_obj.month + months - 1) % 12 + 1
    return datetime(year, month, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        start_month = int(request.form["start_month"])
        start_year = int(request.form["start_year"])
        end_month = int(request.form["end_month"])
        end_year = int(request.form["end_year"])
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)
        results = fetch_visa_bulletin_dates(start_date, end_date)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
