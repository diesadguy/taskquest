from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        help_text='Обязательное поле. Не более 150 символов. Можно использовать буквы, цифры и символы @/./+/-/_.',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    password1 = forms.CharField(
        label='Пароль',
        help_text=(
            'Пароль не должен быть слишком похож на другую личную информацию. '
            'Пароль должен содержать минимум 8 символов. '
            'Пароль не должен быть слишком простым или состоять только из цифр.'
        ),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        help_text='Введите тот же пароль ещё раз для подтверждения.',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='Email'
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Имя пользователя',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        labels = {
            'avatar': 'Аватар',
            'bio': 'О себе',
        }