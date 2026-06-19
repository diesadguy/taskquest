from django.utils import timezone

from tasks.models import Task, Comment
from .models import Achievement, UserAchievement, XPLog


TASK_CREATED_XP = 10
TASK_COMPLETED_XP = 30
BEFORE_DEADLINE_XP = 20
HIGH_PRIORITY_XP = 20
COMMENT_CREATED_XP = 5


def calculate_level(xp):
    return int((xp / 100) ** 0.5) + 1


def add_xp(user, action, amount):
    profile = user.profile
    profile.xp += amount
    profile.level = calculate_level(profile.xp)
    profile.save()

    XPLog.objects.create(
        user=user,
        action=action,
        xp_amount=amount
    )


def update_user_streak(user):
    today = timezone.localdate()
    profile = user.profile

    if profile.last_activity_date == today:
        return

    if profile.last_activity_date == today - timezone.timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1

    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak

    profile.last_activity_date = today
    profile.save()


def register_activity(user):
    update_user_streak(user)
    check_achievements(user)


def reward_task_created(user):
    add_xp(user, 'task_created', TASK_CREATED_XP)
    register_activity(user)


def reward_comment_created(user):
    add_xp(user, 'comment_created', COMMENT_CREATED_XP)
    register_activity(user)


def reward_task_completed(user, task):
    add_xp(user, 'task_completed', TASK_COMPLETED_XP)

    today = timezone.localdate()

    if task.deadline and task.deadline >= today:
        add_xp(user, 'before_deadline', BEFORE_DEADLINE_XP)

    if task.priority == 'high':
        add_xp(user, 'high_priority', HIGH_PRIORITY_XP)

    register_activity(user)


def check_achievements(user):
    achievements = Achievement.objects.all()

    for achievement in achievements:
        already_received = UserAchievement.objects.filter(
            user=user,
            achievement=achievement
        ).exists()

        if already_received:
            continue

        if is_achievement_completed(user, achievement):
            UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )

            if achievement.xp_reward > 0:
                add_xp(
                    user=user,
                    action='achievement_received',
                    amount=achievement.xp_reward
                )


def is_achievement_completed(user, achievement):
    condition_type = achievement.condition_type
    condition_value = achievement.condition_value

    if condition_type == 'tasks_created':
        count = Task.objects.filter(created_by=user).count()
        return count >= condition_value

    if condition_type == 'tasks_completed':
        count = Task.objects.filter(
            assignee=user,
            status='done'
        ).count()
        return count >= condition_value

    if condition_type == 'high_priority_completed':
        count = Task.objects.filter(
            assignee=user,
            status='done',
            priority='high'
        ).count()
        return count >= condition_value

    if condition_type == 'comments_created':
        count = Comment.objects.filter(author=user).count()
        return count >= condition_value

    if condition_type == 'streak_days':
        return user.profile.current_streak >= condition_value

    if condition_type == 'level_reached':
        return user.profile.level >= condition_value

    return False