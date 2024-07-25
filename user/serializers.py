from rest_framework import serializers
from .models import Course, Diary

class CourseSerializer(serializers.ModelSerializer):
    diary = serializers.SerializerMethodField()
    class Meta:
            model = Course
            fields = '__all__'

    def get_diary(self, obj):
        diary = Diary.objects.filter(course=obj).first()
        if diary:
            return DiarySerializer(diary).data
        return None
    


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary