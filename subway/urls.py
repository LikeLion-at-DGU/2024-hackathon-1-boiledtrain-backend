from django.urls import path, include
from rest_framework import routers
from subway import views

app_name = "subway"
urlpatterns = [
    path('random/', views.random_station, name="random_station"),
]