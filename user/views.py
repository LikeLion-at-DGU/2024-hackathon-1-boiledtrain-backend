from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random
from django.conf import settings
from rest_framework import viewsets, mixins
from .serializers import CourseSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Course

# Create your views here.
# M.K 파트
def choose_place(request):
    # 사용자가 프론트 인터페이스에 입력한 장소 이름을 받아와서 구글 api를 통해 검색
    rest_api_key = getattr(settings, 'MAP_KEY')
    #프론트에서 받아올 부분
    subway_station = "돌곶이역"
    place = "길음 롯데리아"
    
    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={rest_api_key}&language=kr"
    location_response = requests.get(location_url).json()
    
    return JsonResponse(location_response)

def add_place(request):

    # choose_place 에서 선택한 장소의 id 를 전달받아서 세부 정보를 가져온 후 db 에 json 형태로 저장
    rest_api_key = getattr(settings, 'MAP_KEY')
    #프론트에서 받아올 부분
    place_id = "경춘선 숲길"
    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={rest_api_key}&language=kr"
    location_response = requests.get(location_url).json()
    
    # if location_response['candidates']:
    #     location = location_response['candidates'][0]['geometry']['location']
    #     lat = location['lat']
    #     lng = location['lng']
    # detail_url = f"https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Crating%2Cformatted_phone_number&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key={rest_api_key}"
    # detail_response = requests.get(detail_url).json()
    return JsonResponse(location_response)


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        return CourseSerializer
    
    def get_queryset(self):
        return Course.objects.filter(user_id=self.request.user.id)
   


