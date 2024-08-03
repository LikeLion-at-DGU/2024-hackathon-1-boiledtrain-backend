import json
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .permissions import IsCourseOwnerOrReadOnly, IsPossibleGetCourseOrReadOnly
from rest_framework.decorators import action

from .models import Course, Diary
from .serializers import CourseSerializer, DiarySerializer, CourseDetailSerializer

from django.shortcuts import get_object_or_404
# 거리 계산에 필요한 라이브러리
from math import radians, sin, cos, sqrt, atan2
class CourseViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        else:
            return CourseSerializer
       
    def get_queryset(self):
        return Course.objects.all()
    
    def get_permissions(self):
        return [IsPossibleGetCourseOrReadOnly()]
    
    @action(methods=['GET'], detail=False, url_path="like_order")
    def like_order(self, request):
        course = self.get_queryset().order_by('-like_count')
        courses = CourseSerializer(course, many=True)
        return Response(courses.data)
    
    @action(methods=['GET'], detail=False, url_path="created_order")
    def created_order(self, request):
        course = self.get_queryset().order_by('created_at')
        courses = CourseSerializer(course, many=True)
        return Response(courses.data)
    
    @action(methods=['GET'], detail=False, url_path="zzim_course")
    def zzim_course(self, request):
        course = self.request.user.likes.all()
        courses = CourseSerializer(course, many=True)
        return Response(courses.data)
    
    @action(methods=['GET'], detail=True, url_path="likes")
    def likes(self, request, pk=None):
        post = self.get_queryset().filter(id=pk).first()
        if request.user in post.like.all():
            post.like.remove(request.user)
            post.like_count -= 1
            post.save()
        else:
            post.like.add(request.user)
            post.like_count += 1
            post.save()
        course_serializer = CourseSerializer(post)
        return Response(course_serializer.data)

class SubwayCourseViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    def get_serializer_class(self):
        return CourseSerializer
       
    def get_queryset(self):
        data = json.loads(self.request.body)
        subway_station = data['subway_station']
        return Course.objects.filter(subway_station=subway_station)
    
    def get_permissions(self):
        return [IsPossibleGetCourseOrReadOnly()]

class MyCourseViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        else:
            return CourseSerializer
    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def get_permissions(self):
        return [IsCourseOwnerOrReadOnly()]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # jwt 토큰으로부터 유저 정보를 전달 받아서 저장
        serializer.save(user=request.user)
        return Response({
            "message " : "코스가 생성되었습니다.",
            "course" : serializer.data    
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success" : "삭제 되었습니다."})

    def perform_destroy(self, instance):
        instance.delete()
    
#다이어리 디테일, 여기서 수정,삭제
class DiaryViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return DiarySerializer
    # permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        return [IsCourseOwnerOrReadOnly()]

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return Diary.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        if Diary.objects.filter(course=course).first() != None:
            return Response({"detail": "Diary already exists for this course."}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, course=course)
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
    def get_queryset(self):

        return Diary.objects.filter(user=self.request.user)

#코스 별 다이어리 (댓글형식으로)
class CourseDiaryViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    def get_permissions(self):
        return [IsCourseOwnerOrReadOnly()]

# permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    def get_serializer_class(self):
        return DiarySerializer
        
    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return Diary.objects.filter(course_id=course_id)
    
    def get_object(self):
        queryset = self.get_queryset()
        course_id = self.kwargs.get("course_id")
        return get_object_or_404(queryset, course_id=course_id)

    def create(self, request, *args, **kwargs):
        
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        if Diary.objects.filter(course=course).first() != None:
            return Response({"detail": "Diary already exists for this course."}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, course=course)
        
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

def haversine(lon1, lat1, lon2, lat2):
    # 지구 반지름 (킬로미터 단위)
    R = 6371.0

    # 위도와 경도를 라디안 단위로 변환
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # 차이 계산
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # 하버사인 공식
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

def is_good(lon1, lat1, lon2, lat2):

    # 두 지점 간 거리 계산
    distance = haversine(lon1, lat1, lon2, lat2)

    # 도보 시간 (시간 단위)
    walking_speed_kmh = 5  # 시속 5킬로미터
    walking_time_hours = 20 / 60  # 20분을 시간 단위로 변환

    # 20분 동안 도보 가능한 최대 거리
    max_walking_distance = walking_speed_kmh * walking_time_hours

    # 거리 비교
    if distance <= max_walking_distance:
        # 도보로 20분 이내면 True 반환
        return True
    else:
        return False

def search_station(subway_station):
    rest_api_key = getattr(settings, 'MAP_KEY')
    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={subway_station}&key={rest_api_key}&language=ko"
    location_response = requests.get(location_url).json()
    
    return location_response

#def search_place(place):
#    rest_api_key = getattr(settings, 'MAP_KEY')
#    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={rest_api_key}&language=ko"
#    location_response = requests.get(location_url).json()
#
#    return location_response


def search_place_by_id(place_id):
    rest_api_key = getattr(settings, 'MAP_KEY')
    place_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={rest_api_key}&language=ko"
    place_response = requests.get(place_url).json()

    return place_response

# 사진 출력 메소드, 미완성
def search_photo(request):
    rest_api_key = getattr(settings, 'MAP_KEY')
    # 최대 넓이
    max_width = 400
    photo_reference = "AelY_Cus4suL2Mw6X9RweWM05EaNMMsw3JpS4J9omAkMZw3_-7bVI4-4KS1-nt-x3tNgQE5Vo23wvFt1I5GAicwA3J-Hg3fc9qEYP1HI0Sah1YvoMKgxipTHshcSTiPJumxOKxnzsBfGfrBJhbdS9qrci62I8Ht3YlfANYQXpkFZ_M-abFQk"
    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={rest_api_key}&language=ko"
    photo_response = requests.get(photo_url)

    if photo_response.status_code == 200:
        # 이미지 데이터를 바로 반환
        return HttpResponse(photo_response.content, content_type='image/jpeg')
    else:
        return HttpResponse('Failed to retrieve the photo', status=photo_response.status_code)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def choose_and_add_place(request):
    # 사용자가 프론트 인터페이스에 입력한 장소 이름을 받아와서 구글 api를 통해 검색

    #프론트에서 받아올 부분
    #정확한 상호명을 받아와야 함
    # json 파일을 받아옴
    data = json.loads(request.body)
    print(data)
    subway_input = data['subway_station']
    place_id = data['place']

    subway_station = search_station(subway_input) # Json 파일
    place = search_place_by_id(place_id) # Json 파일
    
    print(place)
    lng1 = subway_station['results'][0]['geometry']['location']['lng']
    lat1 = subway_station['results'][0]['geometry']['location']['lat']
    lng2 = place['result']['geometry']['location']['lng']
    lat2 = place['result']['geometry']['location']['lat']
    
    def is_good(lng1, lat1, lng2, lat2):
        # 거리 계산 로직을 구현해야 합니다.
        # 예를 들어, Haversine 공식을 사용하여 거리 계산
        from math import radians, cos, sin, sqrt, atan2

        R = 6371.0  # 지구의 반경 (킬로미터 단위)

        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)

        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        # 20분 거리 이내인지 판단 (1분에 80m 가정, 20분 = 1.6km)
        return distance <= 1.6

    if is_good(lng1 , lat1 , lng2 , lat2): # 20분 이내 거리인지 확인
        return JsonResponse({"true" : "등록할 수 있습니다."})
    else:
        return JsonResponse({"false" : "두 지점은 도보로 20분 이상의 거리입니다."})
