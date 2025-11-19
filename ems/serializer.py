from rest_framework import serializers
from ems.models import *

class LoginDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username",required=False)
    class Meta:
        model = LoginDetail
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username",required=False)
    class Meta:
        model =CustomUser
        fields = '__all__'

 