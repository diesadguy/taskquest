from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    xp = models.PositiveIntegerField(
        default=0,
        verbose_name='Опыт'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Уровень'
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name='Текущая серия активности'
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        verbose_name='Лучшая серия активности'
    )
    last_activity_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата последней активности'
    )

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'