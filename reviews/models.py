from django.db import models
from django.conf import settings
from catalog.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

NULLABLE = {'blank': True, 'null': True}


class Review(models.Model):
    """Модель отзыва о товаре"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен модератором')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'Отзыв от {self.user.email} на {self.product.name} (оценка: {self.rating})'

    @property
    def short_text(self):
        """Короткая версия текста отзыва"""
        return self.text[:100] + '...' if len(self.text) > 100 else self.text


class ReviewLike(models.Model):
    """Лайки на отзывы"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Отзыв'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_likes',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        db_table = 'reviews_likes'
        verbose_name = 'Лайк отзыва'
        verbose_name_plural = 'Лайки отзывов'
        unique_together = ('review', 'user')

    def __str__(self):
        return f'{self.user.email} лайкнул отзыв #{self.review.id}'
