from django.urls import path, include
from rest_framework import routers
from accounts import views
from .views import CourseViewSet, choose_place

course_router = routers.SimpleRouter(trailing_slash=False)
course_router.register("course", CourseViewSet, basename="course")

app_name = "user"
urlpatterns = [
    path('', include(course_router.urls)),
    path('choose_place/', choose_place, name="choose_place"),
]