from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('fake-payment/<int:order_id>/', views.FakePaymentView.as_view(), name='fake_payment'),
    path('process-fake-payment/<int:order_id>/', views.ProcessFakePaymentView.as_view(), name='process_fake_payment'),
    path('success/<int:order_id>/', views.OrderSuccessView.as_view(), name='order_success'),

    path('my-orders/', views.UserOrderListView.as_view(), name='user_orders'),
    path('my-orders/<int:pk>/', views.UserOrderDetailView.as_view(), name='user_order_detail'),

    # Повторная оплата
    path('repeat-payment/<int:order_id>/', views.RepeatPaymentView.as_view(), name='repeat_payment'),
]
