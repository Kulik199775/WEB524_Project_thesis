from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone', 'payment_method', 'comment']  # ← payment_method, а не paymant_method
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите полный адрес доставки'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),  # ← исправлено
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Дополнительные пожелания...', 'required': False}),
        }
        labels = {
            'delivery_address': 'Адрес доставки',
            'phone': 'Телефон',
            'payment_method': 'Способ оплаты',
            'comment': 'Комментарий к заказу',
        }
