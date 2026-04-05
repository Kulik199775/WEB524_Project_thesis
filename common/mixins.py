from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(UserPassesTestMixin):
    """Базовый миксин для проверки роли пользователя"""
    allowed_roles = []

    def test_func(self):
        """Проверяет, имеет ли текущий пользователь доступ к представлению"""
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.role in self.allowed_roles or self.request.user.is_superuser

    def handle_no_permission(self):
        """Обрабатывает случай, когда у пользователя нет доступа"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied('У вас нет прав для доступа к этой странице.')


class AdminRequiredMixin(RoleRequiredMixin):
    """Миксин для доступа только админов"""
    allowed_roles = ['admin']


class ModeratorRequiredMixin(RoleRequiredMixin):
    """Миксин для доступа модераторов и администраторов"""
    allowed_roles = ['admin', 'moderator']


class UserIsOwnerMixin(UserPassesTestMixin):
    """Миксин для проверки, является ли текущий пользователь владельцем объекта"""
    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user or self.request.user.role == 'admin'