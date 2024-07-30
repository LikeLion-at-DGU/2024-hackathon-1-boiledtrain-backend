from rest_framework import serializers
from .models import Course, Diary

class CourseSerializer(serializers.ModelSerializer):
    serializers.PrimaryKeyRelatedField(read_only=True)
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


  