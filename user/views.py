from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random
from django.conf import settings
# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permissions import IsOwnerOrReadOnly
from .models import Course, Diary
from .serializers import CourseSerializer, DiarySerializer

from django.shortcuts import get_object_or_404

class CourseViewSet(viewsets.ModelViewSet):
    # queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Course.objects.filter(user=self.request.user)
        return Course.objects.all()
    #아직 로그인 기능이 구현되지 않아 모두가 접근할 수 있도록 설정해놓음

#다이어리 디테일, 여기서 수정,삭제
class DiaryViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    # queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    # permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    permission_classes = [AllowAny]

    def get_queryset(self):
        return Diary.objects.all()
    # def get_queryset(self):
        # return Diary.objects.filter(user=self.request.user) > 확인용으로 모두가 볼 수 있게 해놓음

#코스 별 다이어리 (댓글형식으로)
class CourseDiaryViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [AllowAny]
    serializer_class = DiarySerializer
# permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    def get_object(self):
        course_id = self.kwargs.get("course_id")
        return get_object_or_404(Diary, course_id=course_id)

    def create(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        if Diary.objects.filter(course=course).exists():
            return Response({"detail": "Diary already exists for this course."}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)

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



