from rest_framework import serializers
from cards.models import *

# -----------------------------
#  Contact Details SERIALIZER
# -----------------------------
class ContactDetailsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username",required=False)
    created_by = serializers.CharField(read_only = True)
    class Meta:
        model =ContactDetails
        fields = '__all__'

# -----------------------------
#  QUESTIONS SERIALIZER
# -----------------------------
class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = "__all__"


# -----------------------------
#  QUIZ SUBMISSION SERIALIZER
# -----------------------------
class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = "__all__"


# -----------------------------
#  QUIZ SERIALIZER
# -----------------------------
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"


# -----------------------------
#  TRANSACTION SERIALIZER
# -----------------------------
class TransactionsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.fullname",required=False)
    user_type = serializers.CharField(source="user.usertype",required=False)
    class Meta:
        model = Transactions
        fields = "__all__"


# -----------------------------
#  WALLET SERIALIZER
# -----------------------------
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


# -----------------------------
#  BOOKING SHOW SERIALIZER
# -----------------------------
class BookingShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingShow
        fields = "__all__"