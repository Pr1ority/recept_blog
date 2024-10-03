from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Почта',
                              max_length=254)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True,
                               verbose_name='Аватар')
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message=('Ник содержит недопустимые символы.'
                     ' Допустимы только буквы, цифры, и символы @/./+/-/_.'),
        )],
        verbose_name='Имя пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
