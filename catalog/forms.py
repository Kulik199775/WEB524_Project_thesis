from django import forms
from .models import Product, Category, SkinType, Ingredient


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock', 'image',
            'category', 'skin_types', 'ingredients', 'sku',
            'volume', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Описание товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Артикул'}),
            'volume': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 50 мл'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'skin_types': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'stock': 'Количество на складе',
            'image': 'Изображение',
            'category': 'Категория',
            'skin_types': 'Типы кожи',
            'ingredients': 'Ингредиенты',
            'sku': 'Артикул',
            'volume': 'Объём/Вес',
            'is_active': 'Активен',
        }