"""Request validation for multi-layer autofix demos."""

from __future__ import annotations

from rest_framework import serializers


class BoardDigestQuerySerializer(serializers.Serializer):
    """GET query params for the board digest demo."""

    window = serializers.ChoiceField(
        choices=("today", "week", "all"),
        default="week",
        required=False,
    )
    include_done = serializers.BooleanField(default=False, required=False)


class BulkCompleteSerializer(serializers.Serializer):
    """POST body for bulk-complete demo."""

    todo_ids = serializers.ListField(
        child=serializers.CharField(max_length=64),
        allow_empty=False,
        max_length=50,
        help_text="Todo public ids (UUID strings in the real app).",
    )
    actor = serializers.CharField(max_length=128, required=False, allow_blank=True)


class NotifyPreviewQuerySerializer(serializers.Serializer):
    """GET query params for notify-preview demo."""

    todo_id = serializers.CharField(max_length=64, required=False)
    # When omitted, the service uses a canned unassigned card (still explodes).
