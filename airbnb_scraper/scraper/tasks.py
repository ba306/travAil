import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import Search, SearchResult
from .airbnb_scrape import set_up_driver, scrape_listings
from .utils import normalize_url, load_credentials
from .emailer import send_email
from datetime import timedelta
from threading import Lock
from urllib.parse import urlparse, urlencode, urlunparse

logger = logging.getLogger(__name__)
task_lock = Lock()

@shared_task
def periodic_scrape(search_id):
    with task_lock:
        try:
            search = Search.objects.get(id=search_id)
            start_date_str = search.start_date.strftime('%Y-%m-%d')
            end_date_str = search.end_date.strftime('%Y-%m-%d')

            # Construct search URL
            monthly_length = (search.end_date.year - search.start_date.year) * 12 + (
                    search.end_date.month - search.start_date.month)
            search_url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={start_date_str}&monthly_end_date={end_date_str}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={search.ne_lat}&ne_lng={search.ne_lng}&sw_lat={search.sw_lat}&sw_lng={search.sw_lng}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={monthly_length}&checkin={start_date_str}&checkout={end_date_str}&adults={search.num_adults}&price_max={search.max_price}"

            driver = set_up_driver()
            try:
                # Scrape listings
                current_urls = scrape_listings(driver, search_url, start_date_str, end_date_str)

                if not current_urls:
                    sender_email, sender_password = load_credentials()
                    if sender_email and sender_password:
                        send_email(
                            ["No listings found for the given search parameters."],
                            sender_email,
                            sender_password,
                            search.email,
                            {
                                'start_date': start_date_str,
                                'end_date': end_date_str,
                                'num_adults': search.num_adults,
                                'max_price': search.max_price,
                                'ne_lat': search.ne_lat,
                                'ne_lng': search.ne_lng,
                                'sw_lat': search.sw_lat,
                                'sw_lng': search.sw_lng,
                            }
                        )
                    return

                # Normalize URLs for comparison
                normalized_current_urls = [normalize_url(url) for url in current_urls]

                # Get previous results
                previous_results = SearchResult.objects.filter(
                    search=search
                ).values_list('normalized_url', flat=True)

                # Find new URLs
                new_urls = [url for url in normalized_current_urls if url not in previous_results]

                # Save new results (with normalized URLs for comparison)
                for url, normalized_url in zip(current_urls, normalized_current_urls):
                    if normalized_url in new_urls:
                        SearchResult.objects.create(
                            search=search,
                            url=url,  # Store original URL
                            normalized_url=normalized_url  # Store normalized version for comparison
                        )

                # Prepare full URLs with search parameters for email
                full_urls = []
                for url in current_urls:
                    parsed = urlparse(url)
                    query_params = {
                        'check_in': start_date_str,
                        'check_out': end_date_str,
                        'adults': str(search.num_adults),
                        'price_max': str(search.max_price),
                        'map_bounds': f"{search.sw_lat},{search.sw_lng} {search.ne_lat},{search.ne_lng}"
                    }
                    full_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        urlencode(query_params),
                        parsed.fragment
                    ))
                    full_urls.append(full_url)

                # Prepare search parameters for email
                search_params = {
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'num_adults': search.num_adults,
                    'max_price': search.max_price,
                    'ne_lat': search.ne_lat,
                    'ne_lng': search.ne_lng,
                    'sw_lat': search.sw_lat,
                    'sw_lng': search.sw_lng,
                }

                # Send email with full URLs if new listings found
                sender_email, sender_password = load_credentials()
                if sender_email and sender_password and new_urls:
                    send_email(full_urls, sender_email, sender_password, search.email, search_params, search.id)

            finally:
                driver.quit()

            # Reschedule if needed
            if search.frequency_interval and search.frequency_unit:
                if search.frequency_unit == 'minutes':
                    schedule = timedelta(minutes=search.frequency_interval)
                elif search.frequency_unit == 'hours':
                    schedule = timedelta(hours=search.frequency_interval)
                elif search.frequency_unit == 'days':
                    schedule = timedelta(days=search.frequency_interval)
                elif search.frequency_unit == 'weeks':
                    schedule = timedelta(weeks=search.frequency_interval)

                periodic_scrape.apply_async(
                    args=[search.id],
                    countdown=schedule.total_seconds()
                )

        except ObjectDoesNotExist:
            logger.error(f"Search object with id={search_id} does not exist.")
        except Exception as e:
            logger.error(f"Error in periodic_scrape task: {e}")