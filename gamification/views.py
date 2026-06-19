from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from .models import Achievement, UserAchievement


@login_required
def leaderboard_view(request):
    users = User.objects.select_related('profile').order_by(
        '-profile__xp',
        'username'
    )[:50]

    return render(request, 'gamification/leaderboard.html', {
        'users': users
    })


@login_required
def achievements_view(request):
    all_achievements = Achievement.objects.all()
    received_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement')

    received_ids = received_achievements.values_list(
        'achievement_id',
        flat=True
    )

    return render(request, 'gamification/achievements.html', {
        'all_achievements': all_achievements,
        'received_ids': received_ids,
    })