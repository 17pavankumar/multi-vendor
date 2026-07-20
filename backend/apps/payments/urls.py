from django.urls import path

from apps.payments.views import RazorpayWebhookView, VerifyPaymentView

urlpatterns = [
    path("verify/", VerifyPaymentView.as_view(), name="payment-verify"),
    path("webhook/", RazorpayWebhookView.as_view(), name="payment-webhook"),
]
