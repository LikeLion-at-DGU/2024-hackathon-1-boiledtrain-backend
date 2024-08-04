import json
from rest_framework import serializers
from django.http import JsonResponse
from .models import Course, Diary
from django.conf import settings
import requests
from accounts.serializers import UserInfoSerializer

# from .views import search_place_by_id
def search_place_by_id(place_id):
    rest_api_key = getattr(settings, 'MAP_KEY')
    place_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={rest_api_key}&language=ko"
    place_response = requests.get(place_url).json()
    return place_response

class CourseSerializer(serializers.ModelSerializer):
    serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserInfoSerializer(read_only=True)
    is_like = serializers.SerializerMethodField(read_only=True)

    def get_is_like(self, instance):
        request = self.context.get('request', None)
        if request is not None and request.user in instance.like.all():
            return True
        else:
            return False
            
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'like_count',
            'like',
            'is_like'
        ]
        

class CourseDetailSerializer(serializers.ModelSerializer):
    serializers.PrimaryKeyRelatedField(read_only=True)
    placelist = serializers.SerializerMethodField(read_only=True)
    user = UserInfoSerializer(read_only=True)
    is_like = serializers.SerializerMethodField(read_only=True)

    def get_is_like(self, instance):
        request = self.context.get('request', None)
        if request.user in instance.like.all():
            return True
        else:
            return False
        
    def get_placelist(self, instance):
        place_id_list = instance.placelist
        placelist = []
        for p in place_id_list:
            place = search_place_by_id(p)
            result = {
                "name" : place['result']['name']
            }
            if 'formatted_address' in place['result']:
                result['address'] = place['result']['formatted_address']
            if 'rating' in place['result']:
                result['rating'] = place['result']['rating']
            if 'user_ratings_total' in place['result']:
                result['user_ratings_total'] = place['result']['user_ratings_total']
            if 'types' in place['result']:
                result['types'] = place['result']['types']
            if 'photos' in place['result'] and 'photo_reference' in place['result']['photos'][0]:
                result['photo_reference'] = place['result']['photos'][0]['photo_reference']

            placelist.append(result)

        return placelist
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'like_count',
            'like'
        ]
# class CourseDiarySerializer(serializers.ModelSerializer):
#     diary = serializers.SerializerMethodField()
#     serializers.PrimaryKeyRelatedField(read_only=True)
#     class Meta:
#         model = Course
#         fields = '__all__'
#         read_only_fields = [
#             'id',
#             'user',
#             'created_at',
#             'like_count',
#         ]
        
#     def get_diary(self, obj):
#         diary = Diary.objects.filter(course=obj).first()
#         if diary:
#             return DiarySerializer(diary).data
#         return None
    


class DiarySerializer(serializers.ModelSerializer):
    serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Diary
        fields = '__all__'
        read_only_fields = ['user', 'course']
    
    def get_course(self, obj):
        course = Course.objects.filter(id=obj.course_id).first()
        if course:
            return CourseSerializer(course).data
        return None
    image = serializers.ImageField(use_url=True, required=False)


  