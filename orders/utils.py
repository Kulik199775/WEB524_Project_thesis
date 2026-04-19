from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """
    Отправляет письмо с подтверждением заказа
    Использует те же настройки email, что и для регистрации
    """
    subject = f'Kasmia - Подтверждение заказа #{order.id}'

    # HTML контент письма
    html_message = render_to_string('orders/order_confirmation.html', {
        'order': order,
        'items': order.items.all(),
        'total': order.get_total_cost(),
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
    })

    # Текстовый вариант
    plain_message = strip_tags(html_message)

    # Отправляем письмо (аналогично регистрации)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
        html_message=html_message,
    )