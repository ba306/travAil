from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchForm
from .airbnb_scrape import set_up_driver, scrape_listings
from .emailer import send_email
from .utils import load_credentials, load_previous_urls, save_urls, normalize_url
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

            # Construct URL
            monthly_length = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            url = f"https://www.airbnb.com/s/United-States/homes?refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date={start_date.strftime('%Y-%m-%d')}&monthly_end_date={end_date.strftime('%Y-%m-%d')}&price_filter_input_type=0&channel=EXPLORE&query=United%20States&place_id=ChIJCzYy5IS16lQRQrfeQ5K5Oxw&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=7&ne_lat={ne_lat}&ne_lng={ne_lng}&sw_lat={sw_lat}&sw_lng={sw_lng}&zoom=14.443235035125602&zoom_level=14.443235035125602&search_by_map=true&monthly_length={monthly_length}&checkin={start_date.strftime('%Y-%m-%d')}&checkout={end_date.strftime('%Y-%m-%d')}&adults={num_adults}&price_max={max_price}"

            # Set up the driver
            driver = set_up_driver()

            try:
                # Scrape listings
                current_urls = scrape_listings(driver, url, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

                # Load previous URLs and compare
                previous_urls = load_previous_urls()
                normalized_current_urls = [normalize_url(url) for url in current_urls]
                normalized_previous_urls = [normalize_url(url) for url in previous_urls]

                new_urls = [url for url, normalized_url in zip(current_urls, normalized_current_urls) if normalized_url not in normalized_previous_urls]

                if new_urls:
                    # Send email if new URLs are found
                    sender_email, sender_password = load_credentials()
                    receiver_email = "georgesque360@gmail.com"  # You can set this dynamically or store it in your config
                    send_email(new_urls, sender_email, sender_password, receiver_email)

                    # Save new URLs
                    save_urls(current_urls)

                    return render(request, 'index.html', {'form': form, 'new_urls': new_urls})
                else:
                    return render(request, 'index.html', {'form': form, 'message': "No new listings found."})

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
        })

    return render(request, 'index.html', {'form': form})
