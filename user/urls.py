from django.urls import path, include
from rest_framework import routers
from .views import CourseViewSet, DiaryViewSet, CourseDiaryViewSet, choose_place

from django.conf.urls.static import static
from django.conf import settings

app_name="user"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("courses", CourseViewSet, basename="courses")
default_router.register("diary", DiaryViewSet, basename="diary")

urlpatterns = [
    path('', include(
        default_router.urls)),
    path('course/<int:id>/', CourseViewSet.as_view({'get': 'retrieve'}), name='course-detail'),
    path('course/<int:course_id>/diary/', CourseDiaryViewSet.as_view({'get': 'retrieve', 'post': 'create', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='course-diary'),
    path('choose_place/', choose_place, name="choose_place"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


