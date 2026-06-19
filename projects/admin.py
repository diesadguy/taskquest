from django.contrib import admin

from .models import Project, ProjectInvitation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_type', 'owner', 'created_at')
    list_filter = ('project_type', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    filter_horizontal = ('members',)


@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('project', 'invited_user', 'invited_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = (
        'project__title',
        'invited_user__username',
        'invited_by__username',
    )