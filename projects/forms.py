from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'project_type']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'project_type': 'Тип проекта',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание проекта'
            }),
            'project_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class ProjectInvitationForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите username пользователя'
        })
    )