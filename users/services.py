from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
import random
import string


def send_register_email(email, user=None):
    """Отправка приветственного письма при регистрации"""
    subject = 'Добро пожаловать в Kasmia!'

    if user:
        # HTML письмо с именем пользователя
        context = {
            'email': email,
            'user': user,
            'site_name': 'Kasmia',
            'site_url': 'http://127.0.0.1:8000',
        }
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = strip_tags(html_message)
    else:
        # Простое текстовое письмо
        plain_message = 'Вы успешно зарегистрировались на платформе Kasmia - Натуральная косметика'
        html_message = None

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_new_password(email, new_password, user=None):
    """Отправка нового пароля"""
    subject = 'Ваш новый пароль в Kasmia'

    if user:
        context = {
            'email': email,
            'new_password': new_password,
            'user': user,
            'site_name': 'Kasmia',
        }
        html_message = render_to_string('emails/new_password.html', context)
        plain_message = strip_tags(html_message)
    else:
        plain_message = f'Ваш новый пароль: {new_password}'
        html_message = None

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_verification_code(email, code, user=None):
    """Отправка кода подтверждения для входа"""
    subject = 'Код для входа в Kasmia'

    context = {
        'email': email,
        'code': code,
        'expiry_minutes': getattr(settings, 'VERIFICATION_CODE_EXPIRY_MINUTES', 10),
        'site_name': 'Kasmia',
        'site_url': 'http://127.0.0.1:8000',
    }

    if user:
        context['user'] = user

    html_message = render_to_string('emails/login_code.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def generate_verification_code(length=6):
    """Генерация случайного кода"""
    return ''.join(random.choices(string.digits, k=length))


def is_code_valid(created_at, expiry_minutes=10):
    """Проверка, не истек ли код"""
    if not created_at:
        return False
    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    return timezone.now() < expiry_time


def send_verification_code(email, code, user=None, purpose='login'):
    """Отправка кода подтверждения"""
    if purpose == 'login':
        subject = 'Код для входа в Kasmia'
        message = f'''
        Здравствуйте, {user.first_name or user.email if user else email}!

        Ваш код для входа в Kasmia: {code}

        Код действителен в течение 10 минут.

        Если вы не запрашивали вход, просто проигнорируйте это письмо.

        С уважением,
        Команда Kasmia
        '''
    else:
        subject = 'Код для регистрации в Kasmia'
        message = f'''
        Здравствуйте!

        Ваш код для завершения регистрации в Kasmia: {code}

        Код действителен в течение 10 минут.

        Если вы не регистрировались, просто проигнорируйте это письмо.

        С уважением,
        Команда Kasmia
        '''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )