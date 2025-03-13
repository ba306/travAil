from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if request.method == 'POST':
        # Process the form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        num_adults = int(request.POST.get('num_adults'))
        max_price = float(request.POST.get('max_price'))
        ne_lat = float(request.POST.get('ne_lat'))
        ne_lng = float(request.POST.get('ne_lng'))
        sw_lat = float(request.POST.get('sw_lat'))
        sw_lng = float(request.POST.get('sw_lng'))

        # Call your pipeline or backend logic here
        # process_data(start_date, end_date, num_adults, max_price, ne_lat, ne_lng, sw_lat, sw_lng)

        return HttpResponse(f"Data received: {start_date} - {end_date}, Adults: {num_adults}, Max Price: {max_price}")

    return render(request, 'index.html')
