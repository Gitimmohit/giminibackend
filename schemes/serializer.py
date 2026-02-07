from rest_framework import serializers
from schemes.models import *

class InvestmentSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentScheme
        fields = '__all__'

class UserInvestmentSerializer(serializers.ModelSerializer):
    scheme_type = serializers.CharField(source="scheme.scheme_type",required=False)
    return_amount = serializers.CharField(source="scheme.return_amount",required=False)
    duration_months = serializers.CharField(source="scheme.duration_months",required=False)
    interest_type = serializers.CharField(source="scheme.interest_type",required=False)
    interest_percent = serializers.CharField(source="scheme.interest_percent",required=False)
    title = serializers.CharField(source="scheme.title",required=False)

    class Meta:
        model = UserInvestment
        fields = '__all__'
