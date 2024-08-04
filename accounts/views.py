import json, requests, os
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from rest_framework import status
from rest_framework import viewsets, mixins

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from .models import User

from rest_framework.permissions import IsAuthenticated
from .serializers import UserInfoSerializer


BASE_URL = 'http://3.36.243.22/api/'

# 프론트 주소
client_url = 'http://13.125.69.196:5173'
client_callback_url = client_url + '/kakao/login'

local_front_callback_url = 'http://localhost:5173'
local_client_callback_url = local_front_callback_url + '/kakao/login'
state = getattr(settings, 'STATE')

class Userinfo(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
     
    def get_queryset(self):
        # 토큰에 해당하는 사용자의 정보만 반환
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        return UserInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        # 현재 로그인된 사용자의 정보를 반환
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_image_path = instance.profile_image.path if instance.profile_image else None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if old_image_path and 'profile_image' in request.FILES:
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        return Response(serializer.data)
    def get_object(self):
        # 현재 로그인된 사용자를 반환
        return self.request.user
    
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={client_callback_url}&response_type=code"
    )


@csrf_exempt
def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    # 프론트로부터 받은 코드
    data = json.loads(request.body)
    code = data['code']
    print("code : " , code)
    # 프론트 주소
    redirect_uri = client_callback_url
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()

    print("token JSON:", json.dumps(token_req_json, indent=4, ensure_ascii=False))
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()

    print("Profile JSON:", json.dumps(profile_json, indent=4, ensure_ascii=False))
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    
    kakao_account = profile_json.get('kakao_account')
    # 사용자의 닉네임, 프로필 사진, 섬네일 사진
    properties = profile_json.get('properties')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # 필요한 정보를 가져옴
    email = kakao_account.get('email')
    name = properties.get('nickname')
    nickname = properties.get('nickname')

    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        print("try 에서 출력한 status 값 : " , accept_status)

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        
        return JsonResponse(accept_json)
        
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        print("except 에서 출력한 status 값 : " , accept_status)
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        user = User.objects.get(email=email)
        user.name = name
        user.nickname = nickname
        user.save()
        # Access Token, Refresh token 
        accept_json = accept.json()
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    # 프론트 url 
    callback_url = client_callback_url



#==========================================
# 프론트 로컬 테스트용
def front_kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={local_client_callback_url}&response_type=code"
    )


@csrf_exempt
def front_kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    # 프론트로부터 받은 코드
    data = json.loads(request.body)
    code = data['code']
    print("code : " , code)
    # 프론트 주소
    redirect_uri = local_client_callback_url
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()

    print("token JSON:", json.dumps(token_req_json, indent=4, ensure_ascii=False))
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()

    print("Profile JSON:", json.dumps(profile_json, indent=4, ensure_ascii=False))
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    
    kakao_account = profile_json.get('kakao_account')
    # 사용자의 닉네임, 프로필 사진, 섬네일 사진
    properties = profile_json.get('properties')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # 필요한 정보를 가져옴
    email = kakao_account.get('email')
    name = properties.get('nickname')
    nickname = properties.get('nickname')

    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        print("try 에서 출력한 status 값 : " , accept_status)

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        
        return JsonResponse(accept_json)
        
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        print("except 에서 출력한 status 값 : " , accept_status)
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        user = User.objects.get(email=email)
        user.name = name
        user.nickname = nickname
        user.save()
        # Access Token, Refresh token 
        accept_json = accept.json()
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        return JsonResponse(accept_json)


class front_KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    # 프론트 url 
    callback_url = local_client_callback_url



# 로컬 테스트용 메소드
LOCAL_BASE_URL = 'http://localhost:8000/api/'
LOCAL_KAKAO_CALLBACK_URI = LOCAL_BASE_URL + 'accounts/localkakao/login/callback/'
def local_kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={LOCAL_KAKAO_CALLBACK_URI}&response_type=code&prompt=login"
    )

def local_kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')

    
    code = request.GET.get("code")
    print("code : " , code)
    # 프론트 주소
    redirect_uri = LOCAL_KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()

    print("token JSON:", json.dumps(token_req_json, indent=4, ensure_ascii=False))
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()

    print("Profile JSON:", json.dumps(profile_json, indent=4, ensure_ascii=False))
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    
    kakao_account = profile_json.get('kakao_account')
    # 사용자의 닉네임, 프로필 사진, 섬네일 사진
    properties = profile_json.get('properties')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # 필요한 정보를 가져옴
    email = kakao_account.get('email')
    name = properties.get('nickname')
    nickname = properties.get('nickname')

    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{LOCAL_BASE_URL}accounts/localkakao/login/finish/", data=data)
        accept_status = accept.status_code

        print("try 에서 출력한 status 값 : " , accept_status)

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        
        return JsonResponse(accept_json)
        
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(
            f"{LOCAL_BASE_URL}accounts/localkakao/login/finish/", data=data)
        accept_status = accept.status_code
        print("except 에서 출력한 status 값 : " , accept_status)
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        user = User.objects.get(email=email)
        user.name = name
        user.nickname = nickname
        user.save()
        # Access Token, Refresh token 
        accept_json = accept.json()
        userinfo = {
            "email" : user.email,
            'name' : user.name,
            "nickname" : user.nickname
        }
        accept_json.pop('user', None)
        accept_json['userinfo'] = userinfo
        return JsonResponse(accept_json)


class LocalKakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = LOCAL_KAKAO_CALLBACK_URI
