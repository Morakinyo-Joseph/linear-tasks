from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgMember

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    """
    Org-scoped todos. Lookup by public UUID only; queryset always filtered
    by request.user.organization.
    """

    serializer_class = TodoSerializer
    permission_classes = [IsOrgMember]
    lookup_field = "public_id"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = Todo.objects.filter(
            organization_id=self.request.user.organization_id,
        ).select_related("created_by")
        status_param = self.request.query_params.get("status")
        if status_param in {Todo.Status.OPEN, Todo.Status.DONE}:
            qs = qs.filter(status=status_param)
        priority_param = self.request.query_params.get("priority")
        if priority_param in {
            Todo.Priority.LOW,
            Todo.Priority.MEDIUM,
            Todo.Priority.HIGH,
        }:
            qs = qs.filter(priority=priority_param)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(title__icontains=q.strip())
        return qs

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, public_id=None):
        todo = self.get_object()
        todo.status = Todo.Status.DONE
        todo.save(update_fields=["status", "updated_at"])
        return Response(TodoSerializer(todo).data)
