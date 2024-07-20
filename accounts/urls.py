from django.urls import path, include
from rest_framework import routers
from accounts import views
from .views import Userinfo

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("userinfo", Userinfo, basename="userinfo")

app_name = "accounts"
urlpatterns = [
    path('', include(default_router.urls)),
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/login/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
]