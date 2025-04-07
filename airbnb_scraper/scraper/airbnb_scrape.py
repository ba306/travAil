from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import logging

logger = logging.getLogger(__name__)


def set_up_driver():
    """Configure and return a headless Chrome WebDriver with optimal settings for scraping."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-css")

    driver = webdriver.Chrome(options=options)
    return driver


def scrape_listings(driver, url, start_date, end_date, min_rating=None, min_reviews=None):
    """
    Scrape Airbnb listings with the given parameters.

    Args:
        driver: Selenium WebDriver instance
        url: Airbnb search URL
        start_date: Check-in date as string (YYYY-MM-DD)
        end_date: Check-out date as string (YYYY-MM-DD)
        min_rating: Minimum rating to filter listings (optional)
        min_reviews: Minimum number of reviews to filter listings (optional)

    Returns:
        List of dictionaries containing listing data
    """
    logger.info(f"Scraping listings from {url} for dates {start_date} to {end_date}")
    if min_rating is not None:
        logger.info(f"Applying minimum rating filter: {min_rating}★")
    if min_reviews is not None:
        logger.info(f"Applying minimum reviews filter: {min_reviews} reviews")

    driver.get(url)
    listings_data = []

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
        scroll_attempts = 0
        max_scroll_attempts = 5

        while not match and scroll_attempts < max_scroll_attempts:
            last_count = len_of_page
            time.sleep(2)
            len_of_page = driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
                "var lenOfPage=document.body.scrollHeight;return lenOfPage;"
            )
            if last_count == len_of_page:
                match = True
            scroll_attempts += 1

        # Extract listing elements
        listings = driver.find_elements(By.XPATH, "//div[@itemprop='itemListElement']")
        logger.info(f"Found {len(listings)} listing elements on page")

        for listing in listings:
            try:
                # Get URL
                url_element = listing.find_element(By.XPATH, ".//a[@aria-labelledby and contains(@href, '/rooms/')]")
                url = url_element.get_attribute('href')

                # Skip if dates don't match
                if start_date not in url or end_date not in url:
                    continue

                # Extract price
                try:
                    price_element = listing.find_element(
                        By.XPATH,
                        ".//span[@aria-hidden='true' and contains(text(), '€')]"
                    )
                    price = price_element.text.strip()
                except NoSuchElementException:
                    price = "Price not available"
                    logger.debug("Could not find price element")

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
                except NoSuchElementException:
                    logger.debug("No review information found for listing")
                except Exception as e:
                    logger.warning(f"Error parsing review scores: {e}")

                # Skip if rating doesn't meet minimum requirement
                if min_rating is not None:
                    if rating is None or rating < min_rating:
                        continue

                # Skip if review count doesn't meet minimum requirement
                if min_reviews is not None:
                    if review_count is None or review_count < min_reviews:
                        continue

                # Add listing data
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
            logger.info("No listings found matching all criteria")
        else:
            logger.info(f"Found {len(listings_data)} valid listings after filtering")

        return listings_data

    except TimeoutException:
        logger.error("Timeout occurred while waiting for listings to load")
        # Save page source and screenshot for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("screenshot.png")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}")
        return []