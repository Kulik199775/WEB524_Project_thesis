from django import forms
from .models import Review
from better_profanity import profanity


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

    def clean_text(self):
        """Валидация текста отзыва на наличие запрещенных слов"""
        text = self.cleaned_data.get('text', '')

        if not text or not text.strip():
            raise forms.ValidationError('Отзыв не может быть пустым.')

        # Проверка на минимальную длину
        if len(text.strip()) < 10:
            raise forms.ValidationError('Отзыв должен содержать не менее 10 символов.')

        # Проверка на максимальную длину
        if len(text) > 2000:
            raise forms.ValidationError('Отзыв не должен превышать 2000 символов.')

        # Проверка на запрещенные слова через better-profanity
        if profanity.contains_profanity(text):
            raise forms.ValidationError(
                'Ваш отзыв содержит недопустимые выражения. '
                'Пожалуйста, отредактируйте текст перед отправкой.'
            )

        return text


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
