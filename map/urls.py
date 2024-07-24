from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "map"
urlpatterns = [
    path('search_places/', search_near_places, name="search_places"),
    path('choose_place/', choose_place, name="choose_place"),
]