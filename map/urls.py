from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "map"
urlpatterns = [
    path('search_places/', search_places, name="search_places"),
]