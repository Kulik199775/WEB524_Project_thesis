from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from common.mixins import AdminRequiredMixin
from .models import Product, Category, SkinType, Favorite
from .forms import ProductForm

from cart.cart import Cart


class ProductListView(ListView):
    """Список товаров с пагинацией"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12  # 12 товаров на страницу

    def get_queryset(self):
        """Фильтрация по активным товарам"""
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['skin_types'] = SkinType.objects.all()
        context['title'] = 'Каталог натуральной косметики'

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
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(sku__icontains=query),
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