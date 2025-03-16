from django.shortcuts import render
from .forms import SearchForm
from .airbnb_scrape import set_up_driver, scrape_listings
from .emailer import send_email
from .utils import load_credentials, normalize_url
from .models import Search, SearchResult
from . import config
from datetime import datetime


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # Get form data
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            num_adults = form.cleaned_data['num_adults']
            max_price = form.cleaned_data['max_price']
            ne_lat = form.cleaned_data['ne_lat']
            ne_lng = form.cleaned_data['ne_lng']
            sw_lat = form.cleaned_data['sw_lat']
            sw_lng = form.cleaned_data['sw_lng']
            email = form.cleaned_data['email']

            # Construct URL
            monthly_length = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={start_date.strftime('%Y-%m-%d')}&monthly_end_date={end_date.strftime('%Y-%m-%d')}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={ne_lat}&ne_lng={ne_lng}&sw_lat={sw_lat}&sw_lng={sw_lng}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={monthly_length}&checkin={start_date.strftime('%Y-%m-%d')}&checkout={end_date.strftime('%Y-%m-%d')}&adults={num_adults}&price_max={max_price}"

            # Set up the driver
            driver = set_up_driver()

            try:
                # Scrape listings
                current_urls = scrape_listings(driver, url, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

                # Check if no listings were found
                if not current_urls:
                    return render(request, 'index.html', {'form': form, 'message': "No listings found for the given dates.", 'config': config})

                # Normalize URLs
                normalized_current_urls = [normalize_url(url) for url in current_urls]

                # Save the search
                search = Search(
                    email=email,
                    start_date=start_date,
                    end_date=end_date,
                    num_adults=num_adults,
                    max_price=max_price,
                    ne_lat=ne_lat,
                    ne_lng=ne_lng,
                    sw_lat=sw_lat,
                    sw_lng=sw_lng,
                )
                search.save()
                print("Current Results:", list(normalized_current_urls))

                # Load previous results for the same user (excluding the current search)
                previous_results = SearchResult.objects.filter(search__email=email).exclude(search=search).values_list('normalized_url', flat=True)
                print("Previous Results:", list(previous_results))

                # Find new URLs
                new_urls = [url for url in normalized_current_urls if url not in previous_results]
                print("New URLs:", new_urls)

                # Save the results (skip duplicates for the same user)
                for url, normalized_url in zip(current_urls, normalized_current_urls):
                    if not SearchResult.objects.filter(search__email=email, normalized_url=normalized_url).exists():
                        SearchResult.objects.create(search=search, url=url, normalized_url=normalized_url)

                # Load credentials
                sender_email, sender_password = load_credentials()

                if sender_email and sender_password:
                    if new_urls:
                        # Send email if new URLs are found
                        send_email(new_urls, sender_email, sender_password, email)
                        return render(request, 'index.html', {'form': form, 'new_urls': new_urls, 'config': config})
                    else:
                        # Send email if no new listings are found
                        subject = "No New Airbnb Listings Found"
                        body = "No new listings were found during the latest search."
                        send_email([body], sender_email, sender_password, email)
                        return render(request, 'index.html', {'form': form, 'message': "No new listings found.", 'config': config})
                else:
                    return render(request, 'index.html', {'form': form, 'error': "Email credentials not found.", 'config': config})

            except Exception as e:
                # Handle the error (e.g., log it or show a user-friendly message)
                print(f"Error: {e}")
                return render(request, 'index.html', {'form': form, 'error': "An error occurred while processing your request."})

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
            'map_zoom': 13,                   # Default zoom level
        })

    return render(request, 'index.html', {'form': form, 'config': config})