from rest_framework import serializers


class VerifyPaymentSerializer(serializers.Serializer):
    """The three values Razorpay's checkout widget hands the frontend
    in its success callback — passed straight through to
    services.verify_payment_signature for the real check."""

    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
