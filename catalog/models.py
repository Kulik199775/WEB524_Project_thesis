from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from users.models import NULLABLE


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='URL-метка', **NULLABLE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, **NULLABLE, related_name='children', verbose_name='Родительская категория')
    description = models.TextField(verbose_name='Описание категории', **NULLABLE)
    image = models.ImageField(upload_to='categories/', verbose_name='Изображение категории', **NULLABLE)
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        """Иерархическое название категории"""
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    def get_absolute_url(self):
        """URL для просмотра категории"""
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})


class SkinType(models.Model):
    """Тип кожи"""
    name = models.CharField(max_length=50, verbose_name='Тип кожи')
    slug = models.SlugField(unique=True, verbose_name='URL-метка', **NULLABLE)
    description = models.TextField(verbose_name='Описание типа кожи', **NULLABLE)
    icon = models.CharField(max_length=50, verbose_name='Иконка', **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'catalog_skin_types'
        verbose_name = 'Тип кожи'
        verbose_name_plural = 'Типы кожи'
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты"""
    name = models.CharField(max_length=100, verbose_name='Название ингредиента')
    scientific_name = models.CharField(max_length=200, verbose_name='Научное название', **NULLABLE)
    description = models.TextField(verbose_name='Описание и свойства ингредиента', **NULLABLE)
    benefits = models.TextField(verbose_name='Польза для кожи/волос', **NULLABLE)
    is_natural = models.BooleanField(default=True, verbose_name='Натуральный компонент')
    is_organic = models.BooleanField(default=False, verbose_name='Органический компонент')
    is_allergen = models.BooleanField(default=False, verbose_name='Потенциальный аллерген')
    image = models.ImageField(upload_to='ingredients/', verbose_name='Изображение', **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_ingredients'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Остаток')
    image = models.ImageField(upload_to='catalog/', verbose_name='Изображение', **NULLABLE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, **NULLABLE, related_name='products', verbose_name='Категория')
    skin_types = models.ManyToManyField(SkinType, related_name='products', verbose_name='Подходит для типа кожи')
    ingredients = models.ManyToManyField(Ingredient, related_name='products', verbose_name='Ингредиенты в составе')
    sku = models.CharField(max_length=200, unique=True, verbose_name='Артикул', **NULLABLE)
    volume = models.CharField(max_length=50, verbose_name='Объём/Вес', **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']  # сортировка от новых к старым

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

    @property
    def average_rating(self):
        """Средний рейтинг товара"""
        from django.db.models import Avg
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else 0
        return 0

    @property
    def reviews_count(self):
        """Количество отзывов"""
        return self.reviews.filter(is_approved=True).count()


class Favorite(models.Model):
    """Избранные товары пользователя"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        db_table = 'catalog_favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'
        ordering = ['-created_at']
        unique_together = ('user', 'product')  # один пользователь может добавить в избранное товар только один раз

    def __str__(self):
        return f'{self.user.email} - {self.product.name}'


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    """Очищает кэш при изменении товара"""
    # Удаляем кэш детальной страницы
    cache.delete(f'product_detail_{instance.id}')

    # Удаляем кэш похожих товаров
    cache.delete(f'related_products_{instance.id}')

    cache.delete('categories_list')
    cache.delete('skin_types_list')
    cache.delete('ingredients_list')
