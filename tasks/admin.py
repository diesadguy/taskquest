from django.contrib import admin

from .models import Tag, Task, Comment, TaskFile


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'project')
    list_filter = ('project',)
    search_fields = ('name', 'project__title')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


class TaskFileInline(admin.TabularInline):
    model = TaskFile
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'project',
        'assignee',
        'priority',
        'status',
        'deadline',
        'created_at',
    )
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description', 'project__title')
    filter_horizontal = ('tags',)
    inlines = [CommentInline, TaskFileInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    search_fields = ('text', 'task__title', 'author__username')


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_by', 'uploaded_at')
    search_fields = ('task__title', 'uploaded_by__username')