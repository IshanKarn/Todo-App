from rest_framework.permissions import BasePermission

class IsJWTAuthenticated(BasePermission):
    """
    Allows access only if JWT payload is attached to request.user
    """

    def has_permission(self, request, view):
        return (
            hasattr(request, "user")
            and isinstance(request.user, dict)
            and "user_id" in request.user
        )
