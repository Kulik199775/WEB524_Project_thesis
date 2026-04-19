from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from common.mixins import AdminRequiredMixin
from .models import Product, Category, SkinType, Favorite, Ingredient
from .forms import ProductForm

from cart.cart import Cart


class ProductListView(ListView):
    """Список товаров с пагинацией и фильтрацией"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Фильтр по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Фильтр по типу кожи
        skin_type_slug = self.request.GET.get('skin_type')
        if skin_type_slug:
            queryset = queryset.filter(skin_types__slug=skin_type_slug)

        # Фильтр по цене
        price_min = self.request.GET.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)

        price_max = self.request.GET.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Фильтр по наличию
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'on' or in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)

        # Фильтр по ингредиентам
        ingredient_ids = self.request.GET.getlist('ingredients')
        if ingredient_ids:
            queryset = queryset.filter(ingredients__id__in=ingredient_ids).distinct()

        # Фильтр по рейтингу
        rating_min = self.request.GET.get('rating_min')
        if rating_min:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=rating_min)

        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['skin_types'] = SkinType.objects.all()
        context['ingredients'] = Ingredient.objects.filter(is_natural=True)[:20]  # ← Теперь работает
        context['title'] = 'Каталог натуральной косметики'
        context['cart'] = Cart(self.request)  # Если используете корзину

        # Сохраняем параметры фильтрации для формы
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'skin_type': self.request.GET.get('skin_type', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'rating_min': self.request.GET.get('rating_min', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['skin_types'] = SkinType.objects.all()
        context['ingredients'] = Ingredient.objects.filter(is_natural=True)[:20]
        context['title'] = 'Каталог натуральной косметики'

        # Сохраняем параметры фильтрации для формы
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'skin_type': self.request.GET.get('skin_type', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }

        return context


class CategoryDetailView(ListView):
    """Товары в категории с пагинацией"""
    model = Product
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        # Получаем товары из текущей категории и всех подкатегорий
        categories = [self.category] + list(self.category.children.filter(is_active=True))
        return Product.objects.filter(category__in=categories, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['title'] = f'Категория: {self.category.name}'
        return context


class CategoryListView(ListView):
    """Список всех категорий"""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=True)


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['skin_types'] = SkinType.objects.all()

        # Проверяем, добавлен ли товар в избранное
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                product=self.object
            ).exists()

            # Проверяем, оставлял ли пользователь отзыв
            from reviews.models import Review
            context['user_reviewed'] = Review.objects.filter(
                user=self.request.user,
                product=self.object
            ).exists()
        else:
            context['is_favorite'] = False
            context['user_reviewed'] = False

        # Похожие товары
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]

        context['title'] = self.object.name
        return context


class ProductCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Создание товара (только админ)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" успешно создан!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Редактирование товара (только админ)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Удаление товара (только админ)"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, f'Товар "{product.name}" успешно удалён!')
        return super().delete(request, *args, **kwargs)


class FavoriteListView(LoginRequiredMixin, ListView):
    """Список избранных товаров с пагинацией"""
    model = Favorite
    template_name = 'catalog/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 12
    login_url = 'users:login'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['title'] = 'Мои избранные товары'
        return context


class AddToFavoriteView(LoginRequiredMixin, View):
    """Добавление в избранное"""

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if created:
            messages.success(request, f'Товар "{product.name}" добавлен в избранное!')
        else:
            messages.info(request, f'Товар "{product.name}" уже в избранном')

        return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))


class RemoveFromFavoriteView(LoginRequiredMixin, View):
    """Удаление из избранного"""

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        Favorite.objects.filter(user=request.user, product=product).delete()
        messages.success(request, f'Товар "{product.name}" удалён из избранного!')
        return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))


class SearchResultsView(ListView):
    """Поиск товаров с пагинацией"""
    model = Product
    template_name = 'catalog/search_results.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query),
                is_active=True
            ).distinct()
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['title'] = f'Результаты поиска: {context["query"]}'
        return context


class SkinTypeProductsView(ListView):
    """Товары для определенного типа кожи с пагинацией"""
    model = Product
    template_name = 'catalog/skin_type_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.skin_type = get_object_or_404(SkinType, slug=self.kwargs['slug'])
        return self.skin_type.products.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skin_type'] = self.skin_type
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['title'] = f'Для типа кожи: {self.skin_type.name}'
        return context