from django import forms

from .models import Task, Tag, Comment, TaskFile


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'assignee',
            'deadline',
            'priority',
            'status',
            'tags',
        ]
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'assignee': 'Исполнитель',
            'deadline': 'Дедлайн',
            'priority': 'Приоритет',
            'status': 'Статус',
            'tags': 'Теги',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название задачи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание задачи'
            }),
            'assignee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            self.fields['assignee'].queryset = project.members.all()
            self.fields['tags'].queryset = project.tags.all()


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        labels = {
            'name': 'Название',
            'color': 'Цвет',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Backend'
            }),
            'color': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('secondary', 'Серый'),
                    ('primary', 'Синий'),
                    ('success', 'Зелёный'),
                    ('danger', 'Красный'),
                    ('warning', 'Жёлтый'),
                    ('info', 'Голубой'),
                    ('dark', 'Тёмный'),
                ]
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Комментарий',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите комментарий'
            }),
        }


class TaskFileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = ['file']
        labels = {
            'file': 'Файл',
        }
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }