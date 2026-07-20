import razorpay
from django.conf import settings


def get_client():
    """A thin wrapper so services.py has exactly one place to patch in
    tests (mocking Razorpay's real API) instead of every call site
    constructing its own Client instance."""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
