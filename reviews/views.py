from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from common.mixins import ModeratorRequiredMixin, UserIsOwnerMixin
from .models import Review, ReviewLike
from .forms import ReviewForm, ReviewModerationForm
from catalog.models import Product


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Создание нового отзыва"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_pk'], is_active=True)
        # Проверяем, не оставлял ли пользователь уже отзыв на этот товар
        if Review.objects.filter(user=request.user, product=self.product).exists():
            messages.error(request, 'Вы уже оставляли отзыв на этот товар')
            return redirect('catalog:product_detail', pk=self.product.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = self.product
        form.instance.is_approved = False  # Требует модерации
        messages.success(self.request, 'Ваш отзыв отправлен на модерацию и появится после проверки')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['title'] = f'Оставить отзыв на {self.product.name}'
        return context


class ReviewUpdateView(LoginRequiredMixin, UserIsOwnerMixin, UpdateView):
    """Редактирование отзыва (только владелец)"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def form_valid(self, form):
        # При редактировании отзыв снова отправляется на модерацию
        form.instance.is_approved = False
        messages.success(self.request, 'Отзыв обновлен и отправлен на повторную модерацию')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.product
        context['title'] = 'Редактирование отзыва'
        return context


class ReviewDeleteView(LoginRequiredMixin, UserIsOwnerMixin, DeleteView):
    """Удаление отзыва (только владелец)"""
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Отзыв успешно удален')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.product
        context['title'] = 'Удаление отзыва'
        return context


class ReviewModerationListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    """Список отзывов на модерацию (только модератор и админ)"""
    model = Review
    template_name = 'reviews/review_moderation_list.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        return Review.objects.filter(is_approved=False).select_related('user', 'product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Модерация отзывов'
        context['total_pending'] = self.get_queryset().count()
        return context


class ReviewApproveView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    """Одобрение отзыва модератором"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = True
        review.save()
        messages.success(request, f'Отзыв от {review.user.email} одобрен')
        return redirect('reviews:moderation_list')


class ReviewRejectView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    """Отклонение отзыва модератором (удаление)"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        user_email = review.user.email
        product_name = review.product.name
        review.delete()
        messages.warning(request, f'Отзыв от {user_email} на {product_name} отклонен и удален')
        return redirect('reviews:moderation_list')


class ReviewLikeView(LoginRequiredMixin, View):
    """Поставить/убрать лайк на отзыве"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk, is_approved=True)
        like, created = ReviewLike.objects.get_or_create(review=review, user=request.user)

        if not created:
            like.delete()
            messages.success(request, 'Лайк убран')
        else:
            messages.success(request, 'Отзыв понравился')

        return redirect(request.META.get('HTTP_REFERER', 'catalog:product_detail'))


class UserReviewsView(LoginRequiredMixin, ListView):
    """Список отзывов текущего пользователя"""
    model = Review
    template_name = 'reviews/user_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои отзывы'
        context['approved_count'] = self.get_queryset().filter(is_approved=True).count()
        context['pending_count'] = self.get_queryset().filter(is_approved=False).count()
        return context


class ProductReviewsView(ListView):
    """Список отзывов на товар с пагинацией и статистикой"""
    model = Review
    template_name = 'reviews/product_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=self.kwargs['product_pk'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Review.objects.filter(product=self.product, is_approved=True).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['title'] = f'Отзывы на {self.product.name}'

        # Получаем все одобренные отзывы для статистики
        approved_reviews = Review.objects.filter(product=self.product, is_approved=True)
        total_reviews = approved_reviews.count()
        avg_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Подсчет количества оценок по звездам
        rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in approved_reviews:
            if review.rating in rating_counts:
                rating_counts[review.rating] += 1

        # Подсчет процентов
        rating_percentages = {}
        for star in [5, 4, 3, 2, 1]:
            if total_reviews > 0:
                rating_percentages[star] = round((rating_counts[star] / total_reviews) * 100)
            else:
                rating_percentages[star] = 0

        context['stats'] = {
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 1),
            'rating_counts': rating_counts,
            'rating_percentages': rating_percentages,
        }

        # Проверка, оставлял ли пользователь отзыв
        if self.request.user.is_authenticated:
            context['user_reviewed'] = Review.objects.filter(
                product=self.product,
                user=self.request.user
            ).exists()
        else:
            context['user_reviewed'] = False

        return context