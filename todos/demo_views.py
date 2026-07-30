"""Intentional error endpoints for Insider → incidence → GitHub blame demos."""

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class BoomView(APIView):
    """
    Raise an unhandled exception so DjangoIntegration beams a request footprint.

    Enabled only when DEBUG=True (local demos). Not for production.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        if not settings.DEBUG:
            return JsonResponse({"detail": "Not found."}, status=404)
        raise RuntimeError("linear-tasks intentional boom for Insider StarLink demo")


class NoticeView(APIView):
    """Manual capture without raising (sanity-check that the SDK is live)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        if not settings.DEBUG:
            return JsonResponse({"detail": "Not found."}, status=404)
        import insider

        insider.capture_message(
            "linear-tasks demo notice from /api/v1/demo/notice/",
            level="warning",
        )
        return JsonResponse({"detail": "captured"})
