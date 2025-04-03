from django.urls import path
from . import views

app_name = 'scraper'  # Add this namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('terminate_search/<int:search_id>/', views.terminate_search, name='terminate_search'),
]