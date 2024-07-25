from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

MAX_LEN_NAME = 150
MAX_LEN_EMAIL = 254


class User(AbstractUser):
    """Модель пользователя."""
    REQUIRED_FIELDS = ('username', 'last_name', 'first_name')
    USERNAME_FIELD = 'email'

    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LEN_NAME,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(max_length=MAX_LEN_NAME)
    last_name = models.CharField(max_length=MAX_LEN_NAME)
    email = models.EmailField('Email', max_length=MAX_LEN_EMAIL, unique=True)
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return str(self.username)


class Subscriptions(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='subscribe_to_yourself'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
