from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "map"
urlpatterns = [
    path('search_places_random/', search_places_random, name="search_places_random"),
    path('choose_place/', choose_place, name="choose_place"),
    path('search_places_category/', search_places_category, name="search_places_category"),
]