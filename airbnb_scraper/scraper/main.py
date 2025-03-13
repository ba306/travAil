from scraper.airbnb_scrape import set_up_driver, scrape_listings
from scraper.emailer import send_email
from scraper.utils import load_credentials, load_previous_urls, save_urls, normalize_url
from scraper import config

def check_new_listings():
    driver = set_up_driver()

    # Construct the URL
    monthly_length = (config.end_date.year - config.start_date.year) * 12 + (
                config.end_date.month - config.start_date.month)
    url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={config.START_DATE}&monthly_end_date={config.END_DATE}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={config.NE_LAT}&ne_lng={config.NE_LNG}&sw_lat={config.SW_LAT}&sw_lng={config.SW_LNG}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={monthly_length}&checkin={config.START_DATE}&checkout={config.END_DATE}&adults={config.NUMBER_OF_ADULTS}&price_max={config.MAX_PRICE}"

    # Scrape the listings
    current_urls = scrape_listings(driver, url, config.START_DATE, config.END_DATE)

    # Load previous URLs and compare
    previous_urls = load_previous_urls()
    normalized_current_urls = [normalize_url(url) for url in current_urls]
    normalized_previous_urls = [normalize_url(url) for url in previous_urls]

    new_urls = [url for url, normalized_url in zip(current_urls, normalized_current_urls) if
                normalized_url not in normalized_previous_urls]

    if new_urls:
        print(f"New URLs found: {new_urls}")
        sender_email, sender_password = load_credentials()
        receiver_email = "georgesque360@gmail.com"
        send_email(new_urls, sender_email, sender_password, receiver_email)
        save_urls(current_urls)

    else:
        print("No new URLs found. No email sent.")

    driver.quit()


# Run the script
if __name__ == "__main__":
    check_new_listings()
