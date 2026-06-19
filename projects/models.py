from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('personal', 'Личный'),
        ('team', 'Командный'),
    ]

    title = models.CharField(
        max_length=150,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='personal',
        verbose_name='Тип проекта'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Владелец'
    )
    members = models.ManyToManyField(
        User,
        related_name='member_projects',
        blank=True,
        verbose_name='Участники'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Завершен'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата завершения'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_member(self, user):
        return self.owner == user or self.members.filter(id=user.id).exists()


class ProjectInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='Проект'
    )
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_invitations',
        verbose_name='Приглашённый пользователь'
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_project_invitations',
        verbose_name='Кто пригласил'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Приглашение в проект'
        verbose_name_plural = 'Приглашения в проекты'
        unique_together = ('project', 'invited_user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.invited_user.username} → {self.project.title}'