from flask import Flask, render_template, request
from visa_scraper import fetch_eb2_india_dates
from datetime import datetime
import json
import os
import glob

app = Flask(__name__)

# Load bulletin cache at startup
CACHE_DIR = "bulletins"
bulletins = []
if os.path.isdir(CACHE_DIR):
    for fname in glob.glob(os.path.join(CACHE_DIR, "*.json")):
        with open(fname, "r") as f:
            try:
                bulletins.append(json.load(f))
            except Exception as e:
                print(f"Error loading {fname}: {e}")

@app.route("/", methods=["GET"])
def index():
    results = []
    now = datetime.now()
    # Defaults
    default_end_month = now.month
    default_end_year = now.year
    default_start_month = now.month
    default_start_year = now.year - 1
    # Get from query or use defaults
    start_month = request.args.get("start_month", str(default_start_month))
    start_year = request.args.get("start_year", str(default_start_year))
    end_month = request.args.get("end_month", str(default_end_month))
    end_year = request.args.get("end_year", str(default_end_year))

    # Use cache for the requested range
    if bulletins:
        def parse_bulletin_date_str(s):
            return datetime.strptime(s, "%B %Y")
        start_dt = datetime(int(start_year), int(start_month), 1)
        end_dt = datetime(int(end_year), int(end_month), 1)
        # Filter and sort
        filtered = [r for r in bulletins if start_dt <= parse_bulletin_date_str(r["bulletin_date"]) <= end_dt]
        filtered.sort(key=lambda r: parse_bulletin_date_str(r["bulletin_date"]))
        results = filtered
    else:
        # Fallback: live scrape if cache is empty
        results = fetch_eb2_india_dates(start_month, start_year, end_month, end_year)

    return render_template("index.html", results=results, current_year=now.year,
                           start_month=int(start_month), start_year=int(start_year),
                           end_month=int(end_month), end_year=int(end_year))

if __name__ == "__main__":
    app.run(debug=True)
