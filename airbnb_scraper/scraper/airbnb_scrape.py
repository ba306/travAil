from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Import TimeoutException
import time
import re

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
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-css")

    driver = webdriver.Chrome(options=options)
    return driver


def scrape_listings(driver, url, start_date, end_date):
    driver.get(url)

    try:
        # Wait for the listings to load
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

        # Extract listing data
        listings = driver.find_elements(By.XPATH, "//div[@itemprop='itemListElement']")
        listings_data = []

        for listing in listings:
            try:
                # Get URL
                url_element = listing.find_element(By.XPATH, ".//a[@aria-labelledby and contains(@href, '/rooms/')]")
                url = url_element.get_attribute('href')

                # Skip if dates don't match
                if start_date not in url or end_date not in url:
                    continue

                # Extract price
                price_element = listing.find_element(
                    By.XPATH,
                    ".//span[@aria-hidden='true' and contains(text(), '€')]"
                )
                price = price_element.text.strip()

                # Extract rating and review count
                rating = None
                review_count = None
                try:
                    review_element = listing.find_element(
                        By.XPATH,
                        ".//span[@aria-hidden='true' and contains(text(), '(')]"
                    )
                    review_scores = re.search(r"([\d.]+)\s+\((\d+)\)", review_element.text)
                    if review_scores:
                        rating = float(review_scores.group(1))
                        review_count = int(review_scores.group(2))
                except:
                    pass  # Not all listings have reviews

                listings_data.append({
                    'url': url,
                    'price': price,
                    'rating': rating,
                    'review_count': review_count
                })

            except Exception as e:
                logger.error(f"Error processing listing: {e}")
                continue

        if not listings_data:
            print("No listings found for the given dates.")
            return []

        return listings_data

    except TimeoutException:
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("screenshot.png")
        print("Timeout occurred while waiting for listings to load.")
        return []
