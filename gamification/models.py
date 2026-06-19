from django.db import models
from django.contrib.auth.models import User


class Achievement(models.Model):
    CONDITION_CHOICES = [
        ('tasks_created', 'Создано задач'),
        ('tasks_completed', 'Выполнено задач'),
        ('high_priority_completed', 'Выполнено важных задач'),
        ('comments_created', 'Оставлено комментариев'),
        ('streak_days', 'Дней активности подряд'),
        ('level_reached', 'Достигнут уровень'),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    condition_type = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES,
        verbose_name='Тип условия'
    )
    condition_value = models.PositiveIntegerField(
        verbose_name='Значение условия'
    )
    xp_reward = models.PositiveIntegerField(
        default=0,
        verbose_name='Награда XP'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Иконка'
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['condition_type', 'condition_value']

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Пользователь'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Достижение'
    )
    received_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата получения'
    )

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = ('user', 'achievement')
        ordering = ['-received_at']

    def __str__(self):
        return f'{self.user.username} - {self.achievement.title}'


class XPLog(models.Model):
    ACTION_CHOICES = [
        ('task_created', 'Создание задачи'),
        ('task_completed', 'Выполнение задачи'),
        ('before_deadline', 'Выполнение до дедлайна'),
        ('high_priority', 'Выполнение важной задачи'),
        ('comment_created', 'Комментарий'),
        ('achievement_received', 'Получение достижения'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='xp_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    xp_amount = models.PositiveIntegerField(
        verbose_name='Количество XP'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начисления'
    )

    class Meta:
        verbose_name = 'История XP'
        verbose_name_plural = 'История XP'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: +{self.xp_amount} XP'