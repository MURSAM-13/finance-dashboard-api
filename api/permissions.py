from rest_framework.permissions import BasePermission
from .models import User


class IsActiveUser(BasePermission):
    """Blocks deactivated accounts from doing anything."""

    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, "is_active") and request.user.is_active)


class IsAdmin(IsActiveUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.ADMIN


class IsAnalystOrAbove(IsActiveUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_min_role(User.ANALYST)


class IsViewerOrAbove(IsActiveUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_min_role(User.VIEWER)
