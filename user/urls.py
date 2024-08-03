from django.urls import path, include
from rest_framework import routers
from .views import CourseViewSet, MyCourseViewSet, DiaryViewSet, CourseDiaryViewSet, choose_and_add_place, SubwayCourseViewSet

from django.conf.urls.static import static
from django.conf import settings

app_name="user"

course_router = routers.SimpleRouter(trailing_slash=False)
course_router.register("course", CourseViewSet, basename="course")

my_course_router = routers.SimpleRouter(trailing_slash=False)
my_course_router.register("my_course", MyCourseViewSet, basename="my_course")

subway_course_router = routers.SimpleRouter(trailing_slash=False)
subway_course_router.register("subway_course", SubwayCourseViewSet, basename="subway_course")

diary_router = routers.SimpleRouter(trailing_slash=False)
diary_router.register("diary", DiaryViewSet, basename="diary")

course_diary_router = routers.SimpleRouter(trailing_slash=False)
course_diary_router.register("diary", CourseDiaryViewSet, basename="diary")

urlpatterns = [
    # M.K 파트
    # 코스 관련 url
    path('', include(course_router.urls)),
    path('', include(my_course_router.urls)),
    path('', include(subway_course_router.urls)),
    path('', include(diary_router.urls)),
    # 아래 수정해야함
    path('course/<int:course_id>/', include(course_diary_router.urls)),
    path('choose_and_add_place/', choose_and_add_place, name="choose_and_add_place"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


