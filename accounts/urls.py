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
    # 프론트 로컬 테스트 용
    path('front_kakao/login/', views.front_kakao_login, name='front_kakao_login'),
    path('front_kakao/login/callback/', views.front_kakao_callback, name='front_kakao_callback'),
    path('front_kakao/login/finish/', views.front_KakaoLogin.as_view(), name='front_kakao_login_todjango'),
    # 로컬 테스트 용
    path('localkakao/login/', views.local_kakao_login, name='local_kakao_login'),
    path('localkakao/login/callback/', views.local_kakao_callback, name='local_kakao_callback'),
    path('localkakao/login/finish/', views.LocalKakaoLogin.as_view(), name='local_kakao_login_todjango'),
]