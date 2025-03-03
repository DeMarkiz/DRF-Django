from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import (
    CustomUserViewSet,
    PaymentViewSet,
    PaymentStatusAPIView,
    PaymentCreateAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "users"

router_user = SimpleRouter()
router_payment = SimpleRouter()


router_user.register("user", CustomUserViewSet)
router_payment.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = (
    router_user.urls
    + router_payment.urls
    + [
        path("login/", TokenObtainPairView.as_view(), name="login"),
        path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path(
            "payments/create/", PaymentCreateAPIView.as_view(), name="payments-create"
        ),
        path(
            "payments/",
            PaymentViewSet.as_view({"get": "list", "post": "create"}),
            name="payments-list",
        ),
        path(
            "payments/status/<str:session_id>/",
            PaymentStatusAPIView.as_view(),
            name="payment-status",
        ),
    ]
)
