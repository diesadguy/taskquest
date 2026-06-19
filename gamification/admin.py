from django.contrib import admin

from .models import Achievement, UserAchievement, XPLog


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'condition_type',
        'condition_value',
        'xp_reward',
    )
    list_filter = ('condition_type',)
    search_fields = ('title', 'description')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'received_at')
    list_filter = ('achievement', 'received_at')
    search_fields = ('user__username', 'achievement__title')


@admin.register(XPLog)
class XPLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'xp_amount', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username',)