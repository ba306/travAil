import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Search, SearchResult
from .airbnb_scrape import set_up_driver, scrape_listings
from .utils import normalize_url, load_credentials
from .emailer import send_email
from datetime import timedelta
from threading import Lock

# Configure the logger
logger = logging.getLogger(__name__)

# Lock to prevent duplicate tasks
task_lock = Lock()

@shared_task
def periodic_scrape(search_id):
    """
    Periodic task to scrape Airbnb listings for a specific search.
    """
    with task_lock:  # Acquire the lock to prevent duplicate tasks
        try:
            search = Search.objects.get(id=search_id)
            start_date_str = search.start_date.strftime('%Y-%m-%d')
            end_date_str = search.end_date.strftime('%Y-%m-%d')
            url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={start_date_str}&monthly_end_date={end_date_str}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={search.ne_lat}&ne_lng={search.ne_lng}&sw_lat={search.sw_lat}&sw_lng={search.sw_lng}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={(search.end_date.year - search.start_date.year) * 12 + (search.end_date.month - search.start_date.month)}&checkin={start_date_str}&checkout={end_date_str}&adults={search.num_adults}&price_max={search.max_price}"

            driver = set_up_driver()
            try:
                # Scrape current listings
                current_urls = scrape_listings(driver, url, start_date_str, end_date_str)
                normalized_current_urls = [normalize_url(url) for url in current_urls]

                # Fetch previous results for the specific search (based on coordinates and time interval)
                previous_results = SearchResult.objects.filter(
                    search__email=search.email,
                    search__ne_lat=search.ne_lat,
                    search__ne_lng=search.ne_lng,
                    search__sw_lat=search.sw_lat,
                    search__sw_lng=search.sw_lng,
                    search__start_date=search.start_date,
                    search__end_date=search.end_date,
                ).values_list('normalized_url', flat=True)
                logger.info(f"Previous Results for {search.email}: {list(previous_results)}")

                # Find new URLs (not in previous results)
                new_urls = [url for url in normalized_current_urls if url not in previous_results]
                logger.info(f"New URLs for {search.email}: {new_urls}")

                # Save the new results (skip duplicates for the same search)
                for url, normalized_url in zip(current_urls, normalized_current_urls):
                    if not SearchResult.objects.filter(
                        search__email=search.email,
                        search__ne_lat=search.ne_lat,
                        search__ne_lng=search.ne_lng,
                        search__sw_lat=search.sw_lat,
                        search__sw_lng=search.sw_lng,
                        search__start_date=search.start_date,
                        search__end_date=search.end_date,
                        normalized_url=normalized_url,
                    ).exists():
                        SearchResult.objects.create(search=search, url=url, normalized_url=normalized_url)

                # Load credentials
                sender_email, sender_password = load_credentials()

                # Send email with new listings or a notification if no new listings are found
                if sender_email and sender_password:
                    if new_urls:
                        subject = "New Airbnb Listings Found"
                        body = "\n".join(new_urls)
                    else:
                        subject = "No New Airbnb Listings Found"
                        body = "No new listings were found during the latest search."

                    send_email([body], sender_email, sender_password, search.email)
                    logger.info(f"Email sent to {search.email} with subject: {subject}")
                else:
                    logger.error("Email credentials not found.")

            finally:
                driver.quit()

            # Re-schedule the task for the next run
            if search.frequency_interval and search.frequency_unit:
                if search.frequency_unit == 'minutes':
                    schedule = timedelta(minutes=search.frequency_interval)
                elif search.frequency_unit == 'hours':
                    schedule = timedelta(hours=search.frequency_interval)
                elif search.frequency_unit == 'days':
                    schedule = timedelta(days=search.frequency_interval)
                elif search.frequency_unit == 'weeks':
                    schedule = timedelta(weeks=search.frequency_interval)

                # Re-schedule the task
                periodic_scrape.apply_async(args=[search.id], countdown=schedule.total_seconds())
                logger.info(f"Re-scheduled periodic_scrape task for search_id={search.id} with interval={schedule}")

        except ObjectDoesNotExist:
            logger.error(f"Search object with id={search_id} does not exist.")
        except Exception as e:
            logger.error(f"Error in periodic_scrape task for search_id={search_id}: {e}")
