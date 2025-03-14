from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def set_up_driver():
    options = Options()

    # Add the headless argument
    options.add_argument("--headless")  # Ensure the browser runs in headless mode
    options.add_argument("--disable-gpu")  # Optional: to avoid GPU usage issues
    options.add_argument("--no-sandbox")  # Optional: helps avoid some sandbox issues on Linux
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    return driver


def scrape_listings(driver, url, start_date, end_date):
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@itemprop='itemListElement']")))

    # Scroll to load all listings
    len_of_page = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                                        "var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while not match:
        last_count = len_of_page
        time.sleep(2)
        len_of_page = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"
                                            "var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if last_count == len_of_page:
            match = True

    # Extract listing URLs
    listings = driver.find_elements(By.XPATH, "//a[@aria-labelledby and contains(@href, '/rooms/')]")
    urls = [listing.get_attribute('href') for listing in listings]

    # Filter URLs by check-in and check-out dates
    matching_urls = [url for url in urls if start_date in url and end_date in url]

    return matching_urls
