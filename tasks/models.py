from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from projects.models import Project


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=20,
        default='secondary',
        verbose_name='Цвет Bootstrap'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Проект'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        unique_together = ('name', 'project')
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    title = models.CharField(
        max_length=150,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Проект'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Исполнитель'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Создал'
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дедлайн'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Приоритет'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name='Статус'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='tasks',
        verbose_name='Теги'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата выполнения'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def mark_completed_if_needed(self):
        if self.status == 'done' and self.completed_at is None:
            self.completed_at = timezone.now()

        if self.status != 'done':
            self.completed_at = None


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Задача'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author.username}'


class TaskFile(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Задача'
    )
    file = models.FileField(
        upload_to='task_files/',
        verbose_name='Файл'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_task_files',
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Файл задачи'
        verbose_name_plural = 'Файлы задач'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file.name