from .models import CustomUser, Payment
from rest_framework.serializers import ModelSerializer


class PaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class CustomUserSerializer(ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'


class UserCommonSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ("id", "email")
