from tasks.models import Task, Comment
from gamification.models import UserAchievement, XPLog
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

from django.contrib.auth.forms import AuthenticationForm


class UserLoginForm(AuthenticationForm):
    username = AuthenticationForm.base_fields['username']
    password = AuthenticationForm.base_fields['password']

    username.label = 'Имя пользователя'
    password.label = 'Пароль'

    username.widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Введите имя пользователя'
    })

    password.widget.attrs.update({
        'class': 'form-control',
        'placeholder': 'Введите пароль'
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('project_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена.')
            return redirect('project_list')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


@login_required
def profile_view(request):
    tasks_created_count = Task.objects.filter(
        created_by=request.user
    ).count()

    tasks_completed_count = Task.objects.filter(
        assignee=request.user,
        status='done'
    ).count()

    comments_count = Comment.objects.filter(
        author=request.user
    ).count()

    achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement')

    achievements_count = achievements.count()

    recent_xp_logs = XPLog.objects.filter(
        user=request.user
    )[:10]

    users_by_xp = User.objects.select_related('profile').order_by(
        '-profile__xp',
        'username'
    )

    user_rank = None

    for index, leaderboard_user in enumerate(users_by_xp, start=1):
        if leaderboard_user == request.user:
            user_rank = index
            break

    return render(request, 'accounts/profile.html', {
        'tasks_created_count': tasks_created_count,
        'tasks_completed_count': tasks_completed_count,
        'comments_count': comments_count,
        'achievements': achievements,
        'achievements_count': achievements_count,
        'recent_xp_logs': recent_xp_logs,
        'user_rank': user_rank,
    })


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })