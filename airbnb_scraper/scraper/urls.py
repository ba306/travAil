# airbnb_scraper/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scraper.urls')),  # Include the scraper app's URLs
]
