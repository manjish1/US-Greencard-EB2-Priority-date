from flask import Flask, render_template, request
from visa_scraper import fetch_eb2_india_dates
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    results = []
    from datetime import datetime
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
    if start_month and start_year and end_month and end_year:
        results = fetch_eb2_india_dates(start_month, start_year, end_month, end_year)
    return render_template("index.html", results=results, current_year=now.year,
                           start_month=int(start_month), start_year=int(start_year),
                           end_month=int(end_month), end_year=int(end_year))

if __name__ == "__main__":
    app.run(debug=True)
