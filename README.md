# 🏡 TravAIl ✈️
## 📌 Overview  

<div align="center">

*Do you hate manually checking Airbnbs and hotel sites?* 

*Ever wish you could filter Airbnb hotels with even more options? Let's face it reviews are important!*

*Sometimes, great deals pop up—but they sell out fast. Tired of missing them?*  

*Ever get frustrated finding cheap flights but sky-high hotel prices?*  

*Wish you could optimize your entire travel experience and save time?*  

*Then you're in the right place! 🌍*

</div>

**TravAIl** is a prototype/ongoing project Airbnb scraper that will expand to scrape other hotel databases and flight prices.  
    The goal is to help users find the **cheapest way to travel** by:

    - 🏠 Scraping Airbnb and other hotel listings at user-defined intervals
    - ✈️ Tracking flight prices in real-time
    - 📈 Predicting cheap travel times based on historical data

  <div style="flex: 0 0 50%; display: flex; justify-content: center;">
    <img src="https://github.com/ba306/travAil/raw/main/snapshots/app_screenshot.png" alt="App Screenshot" width="700" />
  </div>
</div>

## 🚀 Features

- **Airbnb Scraper:** Fetches new listings periodically, filter based on review scores and number of reviews
- **Email Alerts:** Notifies users when new listings appear periodically (user-defined intervals)
- **Map Integration:** Dynamically fetches coordinates of listings

---

## 📊 Future Plans

- **Hotel & Flight Data Integration:** Add hotel databases and flight tracking for better price comparison
- **Price Prediction:** Implement machine learning to predict the best times to travel based on historical data

---

## 🛠️ Technologies

- **Backend:** Django, Python
- **Web Scraping:** Requests, Selenium
- **Task Scheduling:** Celery with Celery Beat
- **Database:** SQLite (prototype), PostgreSQL (production)
- **Frontend:** HTML, CSS, JavaScript (potential React integration)
- **Caching & Queuing:** Redis
