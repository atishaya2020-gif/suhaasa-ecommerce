from django.urls import path
from .views import CreateRazorpayOrderAPIView, VerifyRazorpayPaymentAPIView, RazorpayWebhookAPIView

urlpatterns = [
    path("create/", CreateRazorpayOrderAPIView.as_view(), name="payment-create"),
    path("verify/", VerifyRazorpayPaymentAPIView.as_view(), name="payment-verify"),
    path("webhook/", RazorpayWebhookAPIView.as_view(), name="payment-webhook"),
]
