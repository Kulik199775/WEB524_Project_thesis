from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.cache import cache
from django.http import JsonResponse
from common.mixins import AdminRequiredMixin
from .models import Product, Category, SkinType, Favorite, Ingredient
from .forms import ProductForm
from cart.cart import Cart
import hashlib
import json


class ProductListView(ListView):
    """Список товаров с пагинацией, фильтрацией и кэшированием"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_cache_key(self):
        """Генерируем уникальный ключ кэша на основе всех параметров"""
        params = {
            'page': self.request.GET.get('page', 1),
            'category': self.request.GET.get('category', ''),
            'skin_type': self.request.GET.get('skin_type', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'rating_min': self.request.GET.get('rating_min', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
            'ingredients': ','.join(sorted(self.request.GET.getlist('ingredients', []))),
        }

        param_string = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()

        return f'product_list_{param_hash}'

    def get_queryset(self):
        # Пытаемся получить из кэша
        cache_key = self.get_cache_key()
        queryset = cache.get(cache_key)

        if queryset is None:
            # Если нет в кэше - запрашиваем из БД
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

            # Сохраняем в кэш на 10 минут
            cache.set(cache_key, queryset, 60 * 10)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кэшируем категории
        categories = cache.get('categories_list')
        if categories is None:
            categories = list(Category.objects.filter(is_active=True, parent__isnull=True))
            cache.set('categories_list', categories, 60 * 60 * 6)
        context['categories'] = categories

        # Кэшируем типы кожи
        skin_types = cache.get('skin_types_list')
        if skin_types is None:
            skin_types = list(SkinType.objects.all())
            cache.set('skin_types_list', skin_types, 60 * 60 * 6)
        context['skin_types'] = skin_types

        # Кэшируем ингредиенты
        ingredients = cache.get('ingredients_list')
        if ingredients is None:
            ingredients = list(Ingredient.objects.filter(is_natural=True)[:20])
            cache.set('ingredients_list', ingredients, 60 * 60 * 6)
        context['ingredients'] = ingredients

        context['title'] = 'Каталог натуральной косметики'
        context['cart'] = Cart(self.request)

        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'skin_type': self.request.GET.get('skin_type', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'rating_min': self.request.GET.get('rating_min', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }

        if self.request.user.is_authenticated:
            favorite_ids = Favorite.objects.filter(
                user=self.request.user
            ).values_list('product_id', flat=True)
            context['favorite_ids'] = list(favorite_ids)
        else:
            context['favorite_ids'] = []

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
    """Детальная страница товара с кэшированием"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product_id = self.kwargs['pk']
        cache_key = f'product_detail_{product_id}'

        # Пытаемся получить из кэша
        product = cache.get(cache_key)

        if product is None:
            product = super().get_object(queryset)
            cache.set(cache_key, product, 60 * 30)  # 30 минут

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кэшируем категории
        categories = cache.get('categories_list')
        if categories is None:
            categories = list(Category.objects.filter(is_active=True, parent__isnull=True))
            cache.set('categories_list', categories, 60 * 60 * 6)
        context['categories'] = categories

        # Кэшируем типы кожи
        skin_types = cache.get('skin_types_list')
        if skin_types is None:
            skin_types = list(SkinType.objects.all())
            cache.set('skin_types_list', skin_types, 60 * 60 * 6)
        context['skin_types'] = skin_types

        # Проверяем избранное (кэш на 5 минут)
        if self.request.user.is_authenticated:
            favorite_key = f'favorite_{self.request.user.id}_{self.object.id}'
            is_favorite = cache.get(favorite_key)
            if is_favorite is None:
                is_favorite = Favorite.objects.filter(
                    user=self.request.user,
                    product=self.object
                ).exists()
                cache.set(favorite_key, is_favorite, 60 * 5)
            context['is_favorite'] = is_favorite

            # Проверяем, оставлял ли пользователь отзыв
            from reviews.models import Review
            review_key = f'user_review_{self.request.user.id}_{self.object.id}'
            user_reviewed = cache.get(review_key)
            if user_reviewed is None:
                user_reviewed = Review.objects.filter(
                    user=self.request.user,
                    product=self.object
                ).exists()
                cache.set(review_key, user_reviewed, 60 * 10)
            context['user_reviewed'] = user_reviewed
        else:
            context['is_favorite'] = False
            context['user_reviewed'] = False

        # Кэшируем похожие товары
        related_key = f'related_products_{self.object.id}'
        related_products = cache.get(related_key)
        if related_products is None:
            related_products = list(Product.objects.filter(
                category=self.object.category,
                is_active=True
            ).exclude(id=self.object.id)[:4])
            cache.set(related_key, related_products, 60 * 60)  # 1 час
        context['related_products'] = related_products

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

        # Если это AJAX запрос - возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Товар "{product.name}" добавлен в избранное!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Товар "{product.name}" уже в избранном'
                })

        # Обычный POST запрос
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

        # Если это AJAX запрос - возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" удалён из избранного!'
            })

        # Обычный POST запрос
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
