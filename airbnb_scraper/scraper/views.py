import time
import logging
from django.shortcuts import render
from .forms import SearchForm
from .airbnb_scrape import set_up_driver, scrape_listings
from .emailer import send_email
from .utils import load_credentials, normalize_url
from .models import Search, SearchResult
from . import config
from datetime import timedelta
from celery import current_app
from celery.app.control import Control  # For revoking tasks
from .tasks import periodic_scrape

# Configure the logger
logger = logging.getLogger(__name__)

def index(request):
    """
    View to handle the search form and schedule periodic scraping tasks.
    """
    if request.method == 'POST':
        start_time = time.time()  # Start timing
        form = SearchForm(request.POST)
        if form.is_valid():
            # Get form data
            email = form.cleaned_data['email']
            frequency_interval = form.cleaned_data['frequency_interval']
            frequency_unit = form.cleaned_data['frequency_unit']

            # Check if there is an existing search for this email
            existing_search = Search.objects.filter(email=email).first()
            if existing_search:
                # Revoke the existing task if it exists
                if existing_search.task_id:
                    try:
                        control = Control(app=current_app)
                        control.revoke(existing_search.task_id, terminate=True)  # Forcefully terminate the task
                        logger.info(f"Revoked existing task for search_id={existing_search.id} with task_id={existing_search.task_id}")
                    except Exception as e:
                        logger.error(f"Failed to revoke task for search_id={existing_search.id}: {e}")

                # Update the existing search object
                existing_search.start_date = form.cleaned_data['start_date']
                existing_search.end_date = form.cleaned_data['end_date']
                existing_search.num_adults = form.cleaned_data['num_adults']
                existing_search.max_price = form.cleaned_data['max_price']
                existing_search.ne_lat = form.cleaned_data['ne_lat']
                existing_search.ne_lng = form.cleaned_data['ne_lng']
                existing_search.sw_lat = form.cleaned_data['sw_lat']
                existing_search.sw_lng = form.cleaned_data['sw_lng']
                existing_search.frequency_interval = frequency_interval
                existing_search.frequency_unit = frequency_unit
                existing_search.save()  # Save the updated Search object
                logger.info(f"Updated existing search object with id={existing_search.id}")

                # Schedule the new periodic task
                if frequency_interval and frequency_unit:
                    if frequency_unit == 'minutes':
                        schedule = timedelta(minutes=frequency_interval)
                    elif frequency_unit == 'hours':
                        schedule = timedelta(hours=frequency_interval)
                    elif frequency_unit == 'days':
                        schedule = timedelta(days=frequency_interval)
                    elif frequency_unit == 'weeks':
                        schedule = timedelta(weeks=frequency_interval)

                    # Schedule the Celery task
                    task = periodic_scrape.apply_async(args=[existing_search.id], countdown=0)
                    existing_search.task_id = task.id  # Save the task ID to the search object
                    existing_search.save()  # Save the updated Search object with task_id

                    logger.info(f"Scheduled periodic_scrape task for search_id={existing_search.id} with interval={schedule}")

            else:
                # Create a new search object if no existing search is found
                search = Search(
                    email=email,
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                    num_adults=form.cleaned_data['num_adults'],
                    max_price=form.cleaned_data['max_price'],
                    ne_lat=form.cleaned_data['ne_lat'],
                    ne_lng=form.cleaned_data['ne_lng'],
                    sw_lat=form.cleaned_data['sw_lat'],
                    sw_lng=form.cleaned_data['sw_lng'],
                    frequency_interval=frequency_interval,
                    frequency_unit=frequency_unit,
                )
                search.save()  # Save the new Search object
                logger.info(f"Created new search object with id={search.id}")

                # Schedule the new periodic task
                if frequency_interval and frequency_unit:
                    if frequency_unit == 'minutes':
                        schedule = timedelta(minutes=frequency_interval)
                    elif frequency_unit == 'hours':
                        schedule = timedelta(hours=frequency_interval)
                    elif frequency_unit == 'days':
                        schedule = timedelta(days=frequency_interval)
                    elif frequency_unit == 'weeks':
                        schedule = timedelta(weeks=frequency_interval)

                    # Schedule the Celery task
                    task = periodic_scrape.apply_async(args=[search.id], countdown=0)
                    search.task_id = task.id  # Save the task ID to the search object
                    search.save()  # Save the updated Search object with task_id

                    logger.info(f"Scheduled periodic_scrape task for search_id={search.id} with interval={schedule}")

            # Construct URL
            monthly_length = (form.cleaned_data['end_date'].year - form.cleaned_data['start_date'].year) * 12 + (form.cleaned_data['end_date'].month - form.cleaned_data['start_date'].month)
            url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={form.cleaned_data['start_date'].strftime('%Y-%m-%d')}&monthly_end_date={form.cleaned_data['end_date'].strftime('%Y-%m-%d')}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={form.cleaned_data['ne_lat']}&ne_lng={form.cleaned_data['ne_lng']}&sw_lat={form.cleaned_data['sw_lat']}&sw_lng={form.cleaned_data['sw_lng']}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={monthly_length}&checkin={form.cleaned_data['start_date'].strftime('%Y-%m-%d')}&checkout={form.cleaned_data['end_date'].strftime('%Y-%m-%d')}&adults={form.cleaned_data['num_adults']}&price_max={form.cleaned_data['max_price']}"

            # Set up the driver
            driver = set_up_driver()

            try:
                # Scrape listings
                scrape_start_time = time.time()  # Start timing for scraping
                current_urls = scrape_listings(driver, url, form.cleaned_data['start_date'].strftime('%Y-%m-%d'), form.cleaned_data['end_date'].strftime('%Y-%m-%d'))
                scrape_end_time = time.time()  # End timing for scraping
                scrape_duration = scrape_end_time - scrape_start_time
                logger.info(f"Scraping took {scrape_duration:.2f} seconds")

                # Check if no listings were found
                if not current_urls:
                    # Load credentials
                    sender_email, sender_password = load_credentials()

                    if sender_email and sender_password:
                        # Send email if no listings are found
                        subject = "No Airbnb Listings Found"
                        body = "No listings were found for the given search parameters."
                        send_email([body], sender_email, sender_password, email)

                    return render(request, 'index.html', {
                        'form': form,
                        'message': "No listings found for the given dates.",
                        'config': config
                    })

                # Normalize URLs
                normalized_current_urls = [normalize_url(url) for url in current_urls]

                # Fetch previous results for the specific search (based on coordinates and time interval)
                previous_results = SearchResult.objects.filter(
                    search__email=email,
                    search__ne_lat=form.cleaned_data['ne_lat'],
                    search__ne_lng=form.cleaned_data['ne_lng'],
                    search__sw_lat=form.cleaned_data['sw_lat'],
                    search__sw_lng=form.cleaned_data['sw_lng'],
                    search__start_date=form.cleaned_data['start_date'],
                    search__end_date=form.cleaned_data['end_date'],
                ).values_list('normalized_url', flat=True)
                logger.info(f"Previous Results for {email}: {list(previous_results)}")

                # Find new URLs (not in previous results)
                new_urls = [url for url in normalized_current_urls if url not in previous_results]
                logger.info(f"New URLs for {email}: {new_urls}")

                # Save the new results (skip duplicates for the same search)
                for url, normalized_url in zip(current_urls, normalized_current_urls):
                    if not SearchResult.objects.filter(
                        search__email=email,
                        search__ne_lat=form.cleaned_data['ne_lat'],
                        search__ne_lng=form.cleaned_data['ne_lng'],
                        search__sw_lat=form.cleaned_data['sw_lat'],
                        search__sw_lng=form.cleaned_data['sw_lng'],
                        search__start_date=form.cleaned_data['start_date'],
                        search__end_date=form.cleaned_data['end_date'],
                        normalized_url=normalized_url,
                    ).exists():
                        SearchResult.objects.create(search=existing_search if existing_search else search, url=url, normalized_url=normalized_url)

                # Load credentials
                sender_email, sender_password = load_credentials()

                # Send email and return the response
                if new_urls:
                    send_email(new_urls, sender_email, sender_password, email)
                    end_time = time.time()
                    total_duration = end_time - start_time
                    logger.info(f"Total request processing time: {total_duration:.2f} seconds")
                    return render(request, 'index.html', {
                        'form': form,
                        'new_urls': new_urls,
                        'config': config,
                        'scrape_duration': scrape_duration,
                        'total_duration': total_duration
                    })
                else:
                    subject = "No New Airbnb Listings Found"
                    body = "No new listings were found during the latest search."
                    send_email([body], sender_email, sender_password, email)
                    end_time = time.time()
                    total_duration = end_time - start_time
                    logger.info(f"Total request processing time: {total_duration:.2f} seconds")
                    return render(request, 'index.html', {
                        'form': form,
                        'message': "No new listings found.",
                        'config': config,
                        'scrape_duration': scrape_duration,
                        'total_duration': total_duration
                    })

            except Exception as e:
                # Handle the error (e.g., log it or show a user-friendly message)
                logger.error(f"Error: {e}")
                return render(request, 'index.html', {
                    'form': form,
                    'error': "An error occurred while processing your request.",
                    'config': config
                })

            finally:
                driver.quit()

    else:
        # Initialize form with config values for GET requests
        form = SearchForm(initial={
            'start_date': config.start_date.strftime('%Y-%m-%d'),
            'end_date': config.end_date.strftime('%Y-%m-%d'),
            'num_adults': config.NUMBER_OF_ADULTS,
            'max_price': config.MAX_PRICE,
            'ne_lat': config.NE_LAT,
            'ne_lng': config.NE_LNG,
            'sw_lat': config.SW_LAT,
            'sw_lng': config.SW_LNG,
            'map_center_lat': config.NE_LAT,  # Default center latitude
            'map_center_lng': config.NE_LNG,  # Default center longitude
            'map_zoom': 13,  # Default zoom level
        })

    return render(request, 'index.html', {
        'form': form,
        'config': config
    })
