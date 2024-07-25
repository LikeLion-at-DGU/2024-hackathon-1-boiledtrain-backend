from django.shortcuts import render

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