from django.urls import path
from accounts import views
app_name = "accounts"
urlpatterns = [
    path('', views.login, name='login'),
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/login/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
]