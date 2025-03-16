from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Import TimeoutException
import time

def set_up_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Disable sandboxing
    options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images
    options.add_argument("--start-maximized")  # Start maximized
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation control
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Disable automation flags
    options.add_experimental_option('useAutomationExtension', False)  # Disable automation extension

    driver = webdriver.Chrome(options=options)
    return driver

def scrape_listings(driver, url, start_date, end_date):
    driver.get(url)

    try:
        # Wait for the listings to load (increase timeout to 30 seconds)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@itemprop='itemListElement']")))

        # Scroll to load all listings
        len_of_page = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
            "var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
        match = False
        while not match:
            last_count = len_of_page
            time.sleep(2)
            len_of_page = driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
                "var lenOfPage=document.body.scrollHeight;return lenOfPage;"
            )
            if last_count == len_of_page:
                match = True

        # Extract listing URLs
        listings = driver.find_elements(By.XPATH, "//a[@aria-labelledby and contains(@href, '/rooms/')]")
        urls = [listing.get_attribute('href') for listing in listings]

        # Filter URLs by check-in and check-out dates
        matching_urls = [url for url in urls if start_date in url and end_date in url]

        # Check if there are no matching URLs
        if not matching_urls:
            print("No listings found for the given dates.")
            return []

        return matching_urls

    except TimeoutException:
        # Log the page source or take a screenshot for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("screenshot.png")
        print("Timeout occurred while waiting for listings to load.")
        return []