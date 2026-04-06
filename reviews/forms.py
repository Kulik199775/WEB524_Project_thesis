from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма для создания и редактирования отзыва"""

    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Расскажите о своем опыте использования продукта...',
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[(i, f'{i} ★') for i in range(1, 6)])
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [(i, '★' * i) for i in range(1, 6)]


class ReviewModerationForm(forms.ModelForm):
    """Форма для модерации отзыва"""

    class Meta:
        model = Review
        fields = ['is_approved', 'text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'readonly': True
            }),
            'rating': forms.Select(attrs={'class': 'form-select', 'disabled': True}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }