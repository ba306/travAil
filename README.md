# 🏡 TravAIl ✈️

<div style="display: flex; justify-content: space-between; align-items: center;">
  <div style="flex: 1;">
    ## 📌 Overview  
    **TravAIl** is a prototype/ongoing project Airbnb scraper that will expand to scrape other hotel databases and flight prices.  
    The goal is to help users find the **cheapest time to travel** by:

    - 🏠 **Scraping Airbnb listings** automatically
    - 🏨 **Fetching hotel prices** from multiple sources
    - ✈️ **Tracking flight prices** in real-time
    - 📈 **Predicting cheap travel times** based on historical data
  </div>
  <div style="flex: 0 0 50%; display: flex; justify-content: center;">
    <img src="https://github.com/ba306/travAil/raw/main/snapshots/app_screenshot.png" alt="App Screenshot" width="700" />
  </div>
</div>

## 🚀 Features

- **Airbnb Scraper:** Fetches new listings every 6 hours
- **Email Alerts:** Notifies users when new listings appear
- **Map Integration:** Dynamically fetches coordinates of listings

---

## 📊 Future Plans

- **Hotel & Flight Data Integration:** Add hotel databases and flight tracking for better price comparison
- **Price Prediction:** Implement machine learning to predict the best times to travel based on historical data

---

## 🛠️ Technologies Used

- **Backend:** Django, Python
- **Web Scraping:** Requests, BeautifulSoup/Selenium
- **Task Scheduling:** Celery with Celery Beat
- **Database:** SQLite (prototype), PostgreSQL (production)
- **Frontend:** HTML, CSS, JavaScript (potential React integration)
- **Caching & Queuing:** Redis
