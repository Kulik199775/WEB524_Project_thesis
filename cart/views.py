import json
from django.views.generic import View, TemplateView
from django.shortcuts import redirect, get_object_or_404, reverse
from django.http import JsonResponse
from django.contrib import messages
from .cart import Cart
from catalog.models import Product


class CartAddView(View):
    """Добавление товара в корзину"""

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Получаем количество (поддержка JSON)
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                quantity = int(data.get('quantity', 1))
            else:
                quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError, json.JSONDecodeError):
            quantity = 1

        # Проверка наличия
        if not product.is_available:
            if request.headers.get(
                    'X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': f'Товар "{product.name}" отсутствует на складе'
                })
            messages.error(request, f'Товар "{product.name}" отсутствует на складе')
            return redirect('catalog:product_detail', pk=product_id)

        # Добавление в корзину
        if cart.add(product, quantity):
            if request.headers.get(
                    'X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'cart_total': len(cart),
                    'cart_total_price': str(cart.get_total_price())
                })
            messages.success(request, f'Товар "{product.name}" добавлен в корзину')
        else:
            if request.headers.get(
                    'X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': f'Недостаточно товара "{product.name}" на складе. Доступно: {product.stock} шт.'
                })
            messages.error(request, f'Недостаточно товара "{product.name}" на складе')

        return redirect(request.META.get('HTTP_REFERER', reverse('catalog:product_list')))


class CartDetailView(TemplateView):
    """Отображение корзины"""
    template_name = 'cart/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        context['title'] = 'Корзина товаров'
        return context


class CartRemoveView(View):
    """Удаление товара из корзины"""

    def post(self, request, product_id):
        cart = Cart(request)
        cart.remove(product_id)
        messages.success(request, 'Товар удален из корзины')
        return redirect('cart:detail')


class CartUpdateView(View):
    """Обновление количества товара в корзине"""

    def post(self, request, product_id):
        cart = Cart(request)
        quantity = int(request.POST.get('quantity', 1))

        if cart.update(product_id, quantity):
            messages.success(request, 'Количество обновлено')
        else:
            messages.error(request, 'Недостаточно товара на складе')

        return redirect('cart:detail')


class CartClearView(View):
    """Очистка корзины"""

    def post(self, request):
        cart = Cart(request)
        cart.clear()
        messages.success(request, 'Корзина очищена')
        return redirect('cart:detail')
