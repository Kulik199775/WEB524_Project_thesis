from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

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