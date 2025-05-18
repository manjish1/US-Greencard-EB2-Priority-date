[![Build & Deploy](https://github.com/${{github.repository}}/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/${{github.repository}}/actions/workflows/deploy.yml)

# 🇺🇸 EB2 Visa Bulletin Tracker (India)

This is a Flask-based web application that scrapes and displays **EB2 India priority dates** from the U.S. Department of State's Visa Bulletin. It allows users to input a start and end month/year to track the EB2 priority date changes over time, and visualizes the results in both a table and an interactive chart.

---

## 🔧 Features

- 🗓️ User input form for start and end date range (month/year)
- 🧹 Web scraping with BeautifulSoup from official Visa Bulletin pages
- 📊 Interactive chart and tabular display of EB2 India priority dates
- ⚙️ Backend with Flask, HTML templating, and pandas for logic
- 🧩 **Modular, maintainable templates** using Jinja2 includes and inheritance
- 🧪 Automated tests for scraper and date logic

---

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/eb2-visa-bulletin-tracker.git
cd eb2-visa-bulletin-tracker
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## 🚀 Local Development (Static Site)

To preview the static site locally:

1. **Update the data:**
   ```bash
   ./update_bulletin_cache.sh
   ```
   This will generate/update the JSON files in `site/bulletins/`.

2. **Serve the site locally:**
   ```bash
   cd site
   python3 -m http.server 8000
   ```
   This will start a local server at [http://localhost:8000](http://localhost:8000).

3. **Open your browser:**
   Go to [http://localhost:8000](http://localhost:8000) to view the static site.

You can now test all features locally before pushing changes to GitHub.

---

## 🗂️ Project Structure

```
eb2-visa-bulletin-tracker/
│
├── app.py                  # Main Flask app and route
├── visa_scraper.py         # Scraper and date logic
├── requirements.txt        # Python dependencies
├── templates/              # Modular Jinja2 templates
│   ├── base.html           # Base layout (styles, blocks)
│   ├── index.html          # Main page (extends base)
│   ├── form.html           # User input form
│   ├── results_card.html   # Results card (chart + table)
│   ├── results_chart.html  # Chart canvas only
│   └── results_table.html  # Results table only
├── tests/                  # Test suite (pytest)
│   └── test_visa_scraper.py
├── README.md               # Project overview (this file)
├── .gitignore              # Ignore venv, __pycache__, .idea
└── ...
```

---

## 🖥️ UI & Maintainability

- **Responsive, modern UI**: Chart and table are side-by-side on large screens, stacked on mobile.
- **Chart-first design**: The interactive chart is prioritized for quick visual insight.
- **Modular templates**: All major UI sections are split into their own files for easy editing and reuse. Update `form.html`, `results_card.html`, etc. independently.
- **Base template**: Global styles and layout are in `base.html`.

---

## 🧪 Testing

- Tests are in `tests/` and use `pytest` and `requests-mock`.
- To run tests:

```bash
pytest
```

- Coverage includes date logic, scraping, and error handling.

---

## 📝 Example Use Case

You want to track how the EB2 India final action dates moved from **January 2022 to December 2023** — simply input those dates and the app will display the results in a clean table and chart by month.

---

## 🔒 Disclaimer

This application uses public data from the U.S. Department of State. Be mindful not to overload their servers with too many requests in a short time.

---

## 🙋 Author

**Manjish Naik**  
GitHub: https://www.github.com/manjish1  
LinkedIn: https://www.linkedin.com/in/manjish-naik

---

## 📄 License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.
