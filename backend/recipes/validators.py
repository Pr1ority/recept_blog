from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(('Время готовки должно быть не меньше минуты.'),
                              params={'value': value}, )


def validate_ingredients(value):
    if value < 1:
        raise ValidationError((
            'Количество продуктов должно быть не меньше одного.'),
            params={'value': value}, )
