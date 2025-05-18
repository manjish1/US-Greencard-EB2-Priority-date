from flask import Flask, render_template, request
from visa_scraper import fetch_eb2_india_dates
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    results = []
    start_month = request.args.get("start_month")
    start_year = request.args.get("start_year")
    end_month = request.args.get("end_month")
    end_year = request.args.get("end_year")
    if start_month and start_year and end_month and end_year:
        results = fetch_eb2_india_dates(start_month, start_year, end_month, end_year)
    return render_template("index.html", results=results, current_year=datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True)
