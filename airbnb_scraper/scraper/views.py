import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SearchForm
from .models import Search, SearchResult
from . import config
from celery import current_app
from celery.app.control import Control
from .tasks import periodic_scrape
from django.urls import reverse

logger = logging.getLogger(__name__)


def index(request):
    # Initialize form with default values
    form_initial = {
        'start_date': config.start_date.strftime('%Y-%m-%d'),
        'end_date': config.end_date.strftime('%Y-%m-%d'),
        'num_adults': config.NUMBER_OF_ADULTS,
        'max_price': config.MAX_PRICE,
        'ne_lat': config.NE_LAT,
        'ne_lng': config.NE_LNG,
        'sw_lat': config.SW_LAT,
        'sw_lng': config.SW_LNG,
        'map_center_lat': config.NE_LAT,
        'map_center_lng': config.NE_LNG,
        'map_zoom': 13,
        'min_rating': None,
    }

    # Check for termination confirmation
    if 'terminated' in request.GET:
        return render(request, 'index.html', {
            'form': SearchForm(initial=form_initial),
            'message': "Your search has been successfully terminated.",
            'config': config
        })

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Delete any existing searches and their results for this email
            existing_searches = Search.objects.filter(email=email)
            for search in existing_searches:
                if search.task_id:
                    try:
                        control = Control(app=current_app)
                        control.revoke(search.task_id, terminate=True)
                    except Exception as e:
                        logger.error(f"Failed to revoke task: {e}")
                # Associated results will be deleted via CASCADE
                search.delete()

            # Create new search with fresh results
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
                frequency_interval=form.cleaned_data['frequency_interval'],
                frequency_unit=form.cleaned_data['frequency_unit'],
                min_rating=form.cleaned_data['min_rating'],
                min_reviews=form.cleaned_data['min_reviews'],
            )
            search.save()

            # Schedule new task
            task = periodic_scrape.apply_async(args=[search.id], countdown=0)
            search.task_id = task.id
            search.save()

            return render(request, 'index.html', {
                'form': form,
                'message': "Your new search has been scheduled. You'll receive email updates for these specific parameters.",
                'config': config
            })
    else:
        form = SearchForm(initial=form_initial)

    return render(request, 'index.html', {
        'form': form,
        'config': config
    })


def terminate_search(request, search_id):
    try:
        search = Search.objects.get(id=search_id)

        logger.info(f"Terminating search ID {search_id} for email {search.email}")

        # Revoke the Celery task if it exists
        if search.task_id:
            try:
                control = Control(app=current_app)
                control.revoke(search.task_id, terminate=True)
                logger.info(f"Successfully revoked Celery task {search.task_id}")
            except Exception as e:
                logger.error(f"Failed to revoke task {search.task_id}: {e}")

        # Delete the search and its results
        search.delete()
        logger.info(f"Search ID {search_id} and its results have been deleted")

        return redirect(f'{reverse("scraper:index")}?terminated=true')

    except Search.DoesNotExist:
        logger.warning(f"Search ID {search_id} not found - may have already been terminated")
        messages.error(request, "Search not found or already terminated")
        return redirect(reverse("scraper:index"))

