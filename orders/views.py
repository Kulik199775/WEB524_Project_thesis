from django.views.generic import FormView, TemplateView, View, ListView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderForm
from .utils import send_order_confirmation_email


class OrderCreateView(FormView):
    """Оформление заказа"""
    template_name = 'orders/order_create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:fake_payment')

    def dispatch(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0:
            messages.error(request, 'Корзина пуста. Добавьте товары для оформления заказа.')
            return redirect('cart:detail')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        context['title'] = 'Оформление заказа'
        return context

    @transaction.atomic
    def form_valid(self, form):
        cart = Cart(self.request)

        # Создаем заказ
        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            order.user = self.request.user
        order.save()

        # Сохраняем товары из корзины
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Очищаем корзину
        cart.clear()

        # Сохраняем ID заказа в сессии
        self.request.session['order_id'] = order.id

        try:
            send_order_confirmation_email(order)
            messages.success(
                self.request,
                f'Заказ #{order.id} создан! Письмо с подтверждением отправлено на {order.email}'
            )
        except Exception as e:
            # Если письмо не отправилось, показываем предупреждение, но заказ не отменяем
            messages.warning(
                self.request,
                f'Заказ #{order.id} создан, но не удалось отправить письмо. Ошибка: {str(e)}'
            )

        return redirect('orders:fake_payment', order_id=order.id)


class FakePaymentView(TemplateView):
    """Страница оплаты"""
    template_name = 'orders/fake_payment.html'

    def dispatch(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        self.order = get_object_or_404(Order, id=order_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['title'] = 'Оплата заказа'
        return context


class ProcessFakePaymentView(View):
    """Обработка оплаты"""

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Имитация обработки платежа
        card_number = request.POST.get('card_number', '')

        if len(card_number) < 16:
            messages.error(request, 'Неверный номер карты')
            return redirect('orders:fake_payment', order_id=order.id)

        # "Проводим" оплату
        order.status = 'paid'
        order.save()

        # Отправляем письмо об успешной оплате
        try:
            send_order_confirmation_email(order)  # Можно отправить то же письмо или создать отдельное
            messages.success(
                request,
                f'Заказ #{order.id} успешно оплачен! Письмо отправлено на {order.email}'
            )
        except Exception as e:
            messages.success(
                request,
                f'Заказ #{order.id} успешно оплачен! Но не удалось отправить письмо: {str(e)}'
            )

        return redirect('orders:order_success', order_id=order.id)


class OrderSuccessView(TemplateView):
    """Страница успешной оплаты"""
    template_name = 'orders/order_success.html'

    def dispatch(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        self.order = get_object_or_404(Order, id=order_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        context['title'] = 'Заказ оплачен'
        return context


class UserOrderListView(LoginRequiredMixin, ListView):
    """Список заказов пользователя"""
    model = Order
    template_name = 'orders/user_orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои заказы'
        return context


class UserOrderDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о заказе"""
    model = Order
    template_name = 'orders/user_order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Заказ #{self.object.id}'
        return context


class RepeatPaymentView(LoginRequiredMixin, View):
    """Повторная оплата заказа"""

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Проверяем, что заказ не оплачен
        if order.status == 'paid':
            messages.warning(request, 'Этот заказ уже оплачен')
            return redirect('orders:user_order_detail', pk=order.id)

        # Перенаправляем на страницу оплаты
        return redirect('orders:fake_payment', order_id=order.id)
