from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# 커스텀한 유저 모델을 사용한다는 뜻
User = settings.AUTH_USER_MODEL

class Subway(models.Model):
    subway = models.CharField(max_length=50)
# 장소 정보를 출력할 코스를 저장하는 데이터베이스
# placelist 에는 장소의 id 값을 list 형태로 저장한 후 json 필드로 변환하여 저장
# 장소 id 는 외래키가 아니므로 placelist 필드를 이용하는 매소드 실행 시 필수로 DB 에 장소 id 가 존재하는지 검사
# 존재하지 않는다면 즉시 list 에서 id 값을 삭제
class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    subway = models.ForeignKey(Subway, on_delete=models.CASCADE, related_name="courses")
    placelist = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_share = models.BooleanField(default=False)

    def __str__(self):
        return f'Course {self.id} by {self.user.email}'


# 유저가 작성한 일기 정보를 저장할 데이터베이스
# 코스를 외래키로 함
class Diary(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    mood = models.CharField(max_length=50)

    def __str__(self):
        return f'Diary {self.id} by {self.user.email}'