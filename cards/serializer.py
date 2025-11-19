from rest_framework import serializers
from cards.models import *
class ContactDetailsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username",required=False)
    created_by = serializers.CharField(read_only = True)
    class Meta:
        model =ContactDetails
        fields = '__all__'
