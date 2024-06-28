from rest_framework.permissions import BasePermission
from .models import Role


class IsAuthenticatedVerifiedActive(BasePermission):
    """
    Allows access only to authenticated, verified, and active users.
    """

    message = "User must be authenticated, verified, and active."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified and
            request.user.is_active
        )


class IsAdmin(IsAuthenticatedVerifiedActive):
    """
    Allows access only to admin users.
    """

    message = "User must be an admin."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == Role.ADMIN


class IsOrganizer(IsAuthenticatedVerifiedActive):
    """
    Allows access only to organizer users.
    """

    message = "User must be an organizer."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == Role.ORGANIZER


class IsRegularUser(IsAuthenticatedVerifiedActive):
    """
    Allows access only to regular users.
    """

    message = "User must be a regular user."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == Role.USER


class IsAdminOrOrganizer(IsAuthenticatedVerifiedActive):
    """
    Allows access only to admin or organizer users.
    """

    message = "User must be an admin or organizer."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in [Role.ADMIN, Role.ORGANIZER]
    

class IsAdminOrUser(IsAuthenticatedVerifiedActive):
    """
    Allows access only to admin or users.
    """

    message = "User must be an admin or user."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in [Role.ADMIN, Role.USER]


class IsOrganizerOrUser(IsAuthenticatedVerifiedActive):
    """
    Allows access only to organizers or users.
    """

    message = "User must be an organizers or user."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in [Role.ORGANIZER, Role.USER]


class IsAdminOrOrganizerOrUser(IsAuthenticatedVerifiedActive):
    """
    Allows access to admin, organizer, or regular users.
    """

    message = "User must be an admin, organizer, or regular user."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in [Role.ADMIN, Role.ORGANIZER, Role.USER]
