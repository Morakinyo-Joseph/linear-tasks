"""
HTTP entrypoints for multi-layer autofix demos (DEBUG only).

Each view stays thin: validate → service → JSON. Exceptions bubble to the
Insider DjangoIntegration as a multi-frame stack across this package.
"""

from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from . import serializers, services


def _debug_gate():
    if settings.DEBUG:
        return None
    return JsonResponse({"detail": "Not found."}, status=404)


class BoardDigestView(APIView):
    """
    GET /api/v1/demo/complex/board-digest/

    Crosses serializers → services → utils. Explodes on priority weight /
    due-date formatting for the canned high-priority card.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        blocked = _debug_gate()
        if blocked is not None:
            return blocked

        ser = serializers.BoardDigestQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        digest = services.build_board_digest(
            window=ser.validated_data.get("window", "week"),
            include_done=ser.validated_data.get("include_done", False),
        )
        return JsonResponse(digest)


class BulkCompleteView(APIView):
    """
    POST /api/v1/demo/complex/bulk-complete/

    Body: ``{"todo_ids": ["<uuid>", ...], "actor": "optional"}``.
    Explodes in ``utils.parse_todo_ref`` (int cast on UUID strings).
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        blocked = _debug_gate()
        if blocked is not None:
            return blocked

        ser = serializers.BulkCompleteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = services.bulk_complete_todos(
            todo_ids=ser.validated_data["todo_ids"],
            actor=ser.validated_data.get("actor") or "",
        )
        return JsonResponse(result)


class NotifyPreviewView(APIView):
    """
    GET /api/v1/demo/complex/notify-preview/?todo_id=<optional>

    Explodes in ``utils.build_notify_payload`` when assignee is null
    (default canned card).
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        blocked = _debug_gate()
        if blocked is not None:
            return blocked

        ser = serializers.NotifyPreviewQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        preview = services.preview_notify(
            todo_id=ser.validated_data.get("todo_id"),
        )
        return JsonResponse(preview)
