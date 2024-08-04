from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])
        data = {'access_token': str(refresh.access_token)}

        return data
    
class UserInfoSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True, required=False)
    class Meta:
        model = User
        fields = ['email', 'name', 'nickname', 'profile_image']
        read_only_fields = ['email']
    