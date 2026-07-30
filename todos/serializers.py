from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    created_by_id = serializers.UUIDField(source="created_by.public_id", read_only=True)

    class Meta:
        model = Todo
        fields = (
            "id",
            "title",
            "description",
            "status",
            "due_at",
            "created_by_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by_id", "created_at", "updated_at")
