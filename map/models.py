from django.db import models
from django.conf import settings

# 커스텀한 유저 모델을 사용한다는 뜻
User = settings.AUTH_USER_MODEL


# 장소의 카테고리
# 랜덤출력에서 사용되는 카테고리와 동일하게 할 예정
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 구글 맵 장소 데이터를 저장할 모델
# 장소 정보는 속성을 정의하지 않고 json 형태로 저장할 예정
class Place(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    placelnfo = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Place {self.id} by {self.user.email}'

