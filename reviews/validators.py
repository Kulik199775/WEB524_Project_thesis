from django.core.exceptions import ValidationError
from better_profanity import profanity


def validate_no_profanity(value):
    """
    Проверяет текст на наличие нецензурных слов.
    Использует библиотеку better-profanity.
    """
    if not value or not value.strip():
        return

    # Очищаем текст от лишних пробелов
    text_to_check = value.strip()

    if profanity.contains_profanity(text_to_check):
        raise ValidationError(
            'Ваш отзыв содержит недопустимые выражения. '
            'Пожалуйста, отредактируйте текст перед отправкой.'
        )
