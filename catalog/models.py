from django.db import models
from django.core.validators import MinValueValidator

from users.models import NULLABLE


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Остаток')
    image = models.ImageField(upload_to='catalog/', verbose_name='Изображение', **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at'] # сортировка от новых к старым

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        """Проверка на доступность товара для заказа"""
        return self.stock > 0

    def decrease_stock(self, quantity):
        """Уменьшение товара на складе при оформлении заказа"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
