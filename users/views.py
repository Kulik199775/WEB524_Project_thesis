from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from common.mixins import AdminRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json
import random
import string

from .models import User, UserRoles
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserAdminForm, CustomPasswordChangeForm
from .services import send_register_email


def generate_verification_code():
    """Генерация 6-значного кода"""
    return ''.join(random.choices(string.digits, k=6))


def is_password_user(email):
    """Проверка, должен ли пользователь входить по паролю"""
    password_emails = ['admin@example.com', 'moderator@example.com', 'user0@example.com']
    if email in password_emails:
        return True
    if email.endswith('@admin.ru') or email.endswith('@moderator.ru'):
        return True
    return False


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

    def get_object(self, queryset=None):
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

    def get_object(self, queryset=None):
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
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
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
        email = user.email
        is_self = (user == request.user)

        user.delete()

        if is_self:
            messages.success(request, f'Ваш аккаунт {email} успешно удален')
            from django.contrib.auth import logout
            logout(request)
            return redirect('catalog:home')
        else:
            messages.success(request, f'Пользователь {email} успешно удален')
            return redirect('users:user_list')


# ----AJAX вход по коду----

class LoginCodeAjaxView(View):
    """AJAX отправка кода для входа (для обычных пользователей)"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Неверный формат запроса'})

        if not email:
            return JsonResponse({'success': False, 'message': 'Введите email'})

        # Проверяем, не является ли пользователь специальным
        if is_password_user(email):
            return JsonResponse({
                'success': False,
                'message': 'Для этого email используется вход по паролю',
                'redirect_to': reverse('users:login')
            })

        try:
            # Находим или создаем пользователя
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'password': make_password(None),
                    'role': UserRoles.USER
                }
            )

            # Генерируем код
            code = generate_verification_code()

            # Сохраняем в кэш
            cache_key = f'login_code_{email}'
            cache.set(cache_key, {
                'code': code,
                'user_id': user.id,
                'created_at': timezone.now().isoformat()
            }, 600)  # 10 минут

            # Отправляем код на email через VerificationService
            from .services import send_verification_code
            send_verification_code(email, code, user)

            return JsonResponse({
                'success': True,
                'message': 'Код отправлен на email',
                'is_new_user': created
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class RegisterCodeAjaxView(View):
    """AJAX регистрация нового пользователя через код"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Неверный формат запроса'})

        if not email:
            return JsonResponse({'success': False, 'message': 'Введите email'})

        # Проверяем, не зарегистрирован ли уже пользователь
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Пользователь с таким email уже существует. Войдите в аккаунт.'
            })

        # Проверяем, не специальный ли это пользователь
        if is_password_user(email):
            return JsonResponse({
                'success': False,
                'message': 'Для регистрации с этим email используйте обычную форму регистрации',
                'redirect_to': reverse('users:register')
            })

        try:
            # Генерируем код
            code = generate_verification_code()

            # Сохраняем данные пользователя и код в кэш
            cache_key = f'register_code_{email}'
            cache.set(cache_key, {
                'code': code,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': timezone.now().isoformat()
            }, 600)  # 10 минут

            # Отправляем код на email
            from .services import send_verification_code
            # Создаем временного пользователя для отправки
            temp_user = User(email=email, first_name=first_name, last_name=last_name)
            send_verification_code(email, code, temp_user, purpose='register')

            return JsonResponse({
                'success': True,
                'message': 'Код подтверждения отправлен на email'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class VerifyCodeAjaxView(View):
    """Проверка кода и вход/регистрация"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            action = data.get('action', 'login')
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'message': f'Неверный формат запроса: {str(e)}'})

        if not email or not code:
            return JsonResponse({'success': False, 'message': 'Неверные данные'})

        if action == 'login':
            cache_key = f'login_code_{email}'
        else:
            cache_key = f'register_code_{email}'

        # Пробуем получить из кэша, если нет - из сессии
        cached_data = cache.get(cache_key)
        if not cached_data:
            cached_data = request.session.get(cache_key)

        if not cached_data:
            return JsonResponse(
                {'success': False, 'message': 'Код не найден или истек срок действия. Запросите новый код.'})

        if str(cached_data.get('code')) != str(code):
            # Увеличиваем счетчик попыток
            attempts = cached_data.get('attempts', 0) + 1
            cached_data['attempts'] = attempts

            # Сохраняем обратно
            cache.set(cache_key, cached_data, 600)
            request.session[cache_key] = cached_data

            remaining = 3 - attempts
            if remaining <= 0:
                cache.delete(cache_key)
                if cache_key in request.session:
                    del request.session[cache_key]
                return JsonResponse({'success': False, 'message': 'Превышено количество попыток. Запросите новый код.'})

            return JsonResponse({'success': False, 'message': f'Неверный код. Осталось попыток: {remaining}'})

        try:
            if action == 'login':
                # Вход существующего пользователя
                user_id = cached_data.get('user_id')
                if not user_id:
                    return JsonResponse({'success': False, 'message': 'Ошибка: пользователь не найден'})

                user = User.objects.get(id=user_id)
                login(request, user)

                # Очищаем код
                cache.delete(cache_key)
                if cache_key in request.session:
                    del request.session[cache_key]

                return JsonResponse({
                    'success': True,
                    'message': 'Успешный вход',
                    'redirect_url': reverse('catalog:home')
                })

            else:
                # Регистрация нового пользователя
                user_email = cached_data.get('email')
                first_name = cached_data.get('first_name', '')
                last_name = cached_data.get('last_name', '')

                if not user_email:
                    return JsonResponse({'success': False, 'message': 'Ошибка: email не найден'})

                # Проверяем, не существует ли уже пользователь
                if User.objects.filter(email=user_email).exists():
                    return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже существует'})

                user = User(
                    email=user_email,
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRoles.USER,
                    is_active=True
                )
                user.set_unusable_password()  # Устанавливает пустой неиспользуемый пароль
                user.save()

                login(request, user)

                # Очищаем код
                cache.delete(cache_key)
                if cache_key in request.session:
                    del request.session[cache_key]

                # Отправляем приветственное письмо
                try:
                    send_register_email(user_email, user)
                except Exception as e:
                    print(f"Ошибка отправки письма: {e}")

                return JsonResponse({
                    'success': True,
                    'message': 'Регистрация завершена',
                    'redirect_url': reverse('catalog:home')
                })

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Пользователь не найден'})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Ошибка сервера: {str(e)}'})


class ResendCodeAjaxView(View):
    """Повторная отправка кода"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            action = data.get('action', 'login')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Неверный формат запроса'})

        if not email:
            return JsonResponse({'success': False, 'message': 'Email не указан'})

        if action == 'login':
            cache_key = f'login_code_{email}'
        else:
            cache_key = f'register_code_{email}'

        # Пробуем получить из кэша, если нет - из сессии
        cached_data = cache.get(cache_key)
        if not cached_data:
            cached_data = request.session.get(cache_key)

        if not cached_data:
            return JsonResponse({'success': False, 'message': 'Сессия истекла. Начните заново.'})

        # Генерируем новый код
        new_code = generate_verification_code()
        cached_data['code'] = new_code
        cached_data['attempts'] = 0

        # Сохраняем обратно
        cache.set(cache_key, cached_data, 600)
        request.session[cache_key] = cached_data

        # Отправляем новый код
        try:
            if action == 'login':
                user_id = cached_data.get('user_id')
                if user_id:
                    _ = User.objects.get(id=user_id)
                    send_mail(
                        subject='Новый код для входа в Kasmia',
                        message=f'Ваш новый код для входа: {new_code}\nКод действителен 10 минут.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                else:
                    send_mail(
                        subject='Новый код для входа в Kasmia',
                        message=f'Ваш новый код для входа: {new_code}\nКод действителен 10 минут.',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        fail_silently=False,
                    )
            else:
                send_mail(
                    subject='Новый код для регистрации в Kasmia',
                    message=f'Ваш новый код для регистрации: {new_code}\nКод действителен 10 минут.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка отправки: {str(e)}'})

        return JsonResponse({'success': True, 'message': 'Новый код отправлен на ваш email'})
