# 🇺🇸 EB2 Visa Bulletin Tracker (India)

This is a Flask-based web application that scrapes and displays **EB2 India priority dates** from the U.S. Department of State’s Visa Bulletin. It allows users to input a start and end month/year to track the EB2 priority date changes over time.

---

## 🔧 Features

- 🗓️ User input form for start and end date range (month/year)
- 🧹 Web scraping with BeautifulSoup from official Visa Bulletin pages
- 📊 Tabular display of EB2 India priority dates
- ⚙️ Backend with Flask, HTML templating, and pandas for logic

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
pip install flask requests beautifulsoup4 pandas
```


### 4. Run the App

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## 🗂️ Project Structure

```
eb2-visa-bulletin-tracker/
│
├── app.py                  # Main Flask app and scraper logic
├── templates/
│   └── index.html          # Web form and result table
├── README.md               # Project overview (this file)
```

---

## 📝 Example Use Case

You want to track how the EB2 India final action dates moved from **January 2022 to December 2023** — simply input those dates and the app will display the results in a clean table by month.

Input the dates as 01 2022 and 12 2023 in respective input boxes.

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
