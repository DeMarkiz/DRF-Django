from rest_framework import viewsets, generics
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from users import services
from .models import CustomUser, Payment
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsUser
from .serializers import PaymentSerializer, UserCommonSerializer, CustomUserSerializer
from users.permissions import IsModer, IsOwner, IsUser


class CustomUserViewSet(viewsets.ModelViewSet):
    model = CustomUser
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if (
            self.action in ("retrieve", "update", "partial_update", "destroy")
            and self.request.user.email == self.get_object().email
        ):
            return CustomUserSerializer
        return UserCommonSerializer

    def get_permissions(self):
        """Права на действия пользователя"""

        if self.action in ("update", "partial_update", "destroy"):
            permission_classes = [IsAuthenticated, IsUser]
        elif self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class PaymentCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ~IsModer]
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        materials = payment.paid_course or payment.paid_lesson
        stripe_service = services.StripeCheckout(content=materials)
        stripe_service.create_product()
        stripe_service.create_price(amount=payment.amount)
        session_id, payment_link = stripe_service.create_session()
        payment.session_id = session_id
        payment.link = payment_link
        payment.save()


class PaymentViewSet(viewsets.ModelViewSet):
    model = Payment
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "method"]
    orderind_fields = ["payment_date"]


    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user)


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsUser | IsModer]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Успешный запрос",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'session_id': openapi.Schema(type=openapi.TYPE_STRING, title='ID сессии'),
                        'payment_status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            title='Статус платежа',
                            enum=['unpaid', 'paid'],
                            read_only=True,
                        ),
                    }
                )
            ),
        }
    )
    def get(self, request, session_id):
        try:
            payment = Payment.objects.get(session_id=session_id)
        except Payment.DoesNotExist:
            raise NotFound('Платеж с указанным session_id не найден')
        # Запуск проверки разрешений для конкретного объекта
        obj = payment.paid_course or payment.paid_lesson
        self.check_object_permissions(request, obj)
        payment_status = services.retrieve_payment_status(session_id=session_id)
        if payment.status != payment_status:
            payment.status = payment_status
            payment.save()
        return Response({
            'session_id': session_id,
            'payment_status': payment_status,
        })