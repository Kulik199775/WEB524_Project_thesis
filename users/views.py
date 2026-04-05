from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View, DeleteView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from common.mixins import AdminRequiredMixin
from .models import User, UserRoles
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserAdminForm, CustomPasswordChangeForm


class UserRegistrationView(CreateView):
    """Регистрация пользователя"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать, {user.email}')
        return response


class UserLoginView(LoginView):
    """Вход в систему"""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно вошли в систему')
        return reverse_lazy('catalog:home')


class UserLogoutView(LogoutView):
    """Выход из системы"""
    next_page = reverse_lazy('catalog:home')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы вышли из системы')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, DetailView):
    """Просмотр профиля пользователя"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset = None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мой профиль'
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset = None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Профиль успешно обновлен')
        return reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        return context


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Смена пароля"""
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен')
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Список пользователей (для админа)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 5

    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Управление пользователями'
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['admins'] = User.objects.filter(role=UserRoles.ADMIN).count()
        context['moderators'] = User.objects.filter(role=UserRoles.MODERATOR).count()
        context['regular_users'] = User.objects.filter(role=UserRoles.USER).count()
        return context


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Детальная информация о пользователе (только админ)"""
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Пользователь: {self.object.email}'
        return context


class UserEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Редактирование пользователя админов"""
    model = User
    form_class = UserAdminForm
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('users:user_list')

    def form_valid(self, form):
        messages.success(self.request, f'Пользователь {form.instance.email} обновлен')
        return super().form_valid(form)


class UserToggleActiveView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Блокировка/разблокировка пользователя"""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()

        status = 'активирован' if user.is_active else 'заблокирован'
        messages.success(request, f'Пользователь {user.email} {status}')
        return redirect('users:user_list')


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Удаление пользователя"""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'Вы не можете удалить самого себя')
        else:
            email = user.email
            user.delete()
            messages.success(request, f'Пользователь {email} удален')
        return redirect('users:user_list')