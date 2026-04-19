from django.db import models
from django.conf import settings
from catalog.models import Product
from django.core.validators import MinValueValidator

NULLABLE = {'blank': True, 'null': True}


class Order(models.Model):
    """Модель заказа"""

    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтверждён'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )

    PAYMENT_CHOICES = (
        ('cash', 'Наличными при получении'),
        ('card', 'Банковской картой'),
        ('online', 'Онлайн-платеж'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус заказа')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash',
                                      verbose_name='Способ оплаты')
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    phone = models.CharField(max_length=50, verbose_name='Телефон')
    comment = models.TextField(verbose_name='Комментарий к заказу', **NULLABLE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Общая сумма')

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от {self.user.email}'

    def update_total_price(self):
        """Обновление общей суммы заказа"""
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()
        return total
