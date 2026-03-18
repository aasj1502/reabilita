from rest_framework.permissions import BasePermission


class IsEquipeSaudeOuStaff(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        militar = getattr(user, "militar", None)
        return bool(militar and hasattr(militar, "perfil_saude"))
