from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    """Authenticated user with an active organization."""

    message = "Authentication and organization membership are required."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        return getattr(user, "organization_id", None) is not None
