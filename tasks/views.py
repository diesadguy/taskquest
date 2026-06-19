import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from gamification.services import (
    reward_task_created,
    reward_task_completed,
    reward_comment_created,
)

from projects.models import Project
from .forms import TaskForm, TagForm, CommentForm, TaskFileForm
from .models import Task, Tag


def user_has_project_access(project, user):
    return project.is_member(user)


@login_required
def task_create_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этому проекту.')
        return redirect('project_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)

        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.mark_completed_if_needed()
            task.save()
            form.save_m2m()

            reward_task_created(request.user)

            if task.status == 'done':
                reward_task_completed(request.user, task)

            messages.success(request, 'Задача успешно создана.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(project=project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'title': 'Создание задачи'
    })


@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этой задаче.')
        return redirect('project_list')

    comment_form = CommentForm()
    file_form = TaskFileForm()

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'project': project,
        'comment_form': comment_form,
        'file_form': file_form,
    })


@login_required
def task_update_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этой задаче.')
        return redirect('project_list')

    if request.method == 'POST':
        old_status = task.status

        form = TaskForm(request.POST, instance=task, project=project)

        if form.is_valid():
            task = form.save(commit=False)
            task.mark_completed_if_needed()
            task.save()
            form.save_m2m()

            if old_status != 'done' and task.status == 'done':
                reward_task_completed(request.user, task)

            messages.success(request, 'Задача успешно обновлена.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, project=project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'project': project,
        'task': task,
        'title': 'Редактирование задачи'
    })


@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этой задаче.')
        return redirect('project_list')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача успешно удалена.')
        return redirect('project_detail', project_id=project.id)

    return render(request, 'tasks/task_confirm_delete.html', {
        'task': task,
        'project': project,
    })


@login_required
def tag_create_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этому проекту.')
        return redirect('project_list')

    if request.method == 'POST':
        form = TagForm(request.POST)

        if form.is_valid():
            tag = form.save(commit=False)
            tag.project = project
            tag.save()

            messages.success(request, 'Тег успешно создан.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = TagForm()

    return render(request, 'tasks/tag_form.html', {
        'form': form,
        'project': project,
    })


@login_required
def comment_create_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этой задаче.')
        return redirect('project_list')

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()



            reward_comment_created(request.user)

            messages.success(request, 'Комментарий добавлен.')

    return redirect('task_detail', task_id=task.id)


@login_required
def file_upload_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этой задаче.')
        return redirect('project_list')

    if request.method == 'POST':
        form = TaskFileForm(request.POST, request.FILES)

        if form.is_valid():
            task_file = form.save(commit=False)
            task_file.task = task
            task_file.uploaded_by = request.user
            task_file.save()

            messages.success(request, 'Файл загружен.')

    return redirect('task_detail', task_id=task.id)

@login_required
def kanban_board_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not user_has_project_access(project, request.user):
        messages.error(request, 'У вас нет доступа к этому проекту.')
        return redirect('project_list')

    todo_tasks = project.tasks.filter(status='todo')
    in_progress_tasks = project.tasks.filter(status='in_progress')
    review_tasks = project.tasks.filter(status='review')
    done_tasks = project.tasks.filter(status='done')

    return render(request, 'tasks/kanban_board.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'done_tasks': done_tasks,
    })


@login_required
@require_POST
def update_task_status_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if not user_has_project_access(project, request.user):
        return JsonResponse({
            'success': False,
            'error': 'Нет доступа'
        }, status=403)

    try:
        data = json.loads(request.body)
        new_status = data.get('status')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные'
        }, status=400)

    allowed_statuses = ['todo', 'in_progress', 'review', 'done']

    if new_status not in allowed_statuses:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный статус'
        }, status=400)

    old_status = task.status

    task.status = new_status
    task.mark_completed_if_needed()
    task.save()

    if old_status != 'done' and task.status == 'done':
        reward_task_completed(request.user, task)

    return JsonResponse({
        'success': True,
        'new_status': task.status,
    })

@login_required
def my_tasks_view(request):
    tasks = Task.objects.filter(
        assignee=request.user
    ).select_related('project', 'created_by')

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    active_tasks = tasks.exclude(status='done')
    completed_tasks = tasks.filter(status='done')

    total_tasks_count = tasks.count()
    active_tasks_count = active_tasks.count()
    completed_tasks_count = completed_tasks.count()
    overdue_tasks_count = tasks.filter(
        deadline__lt=timezone.localdate()
    ).exclude(
        status='done'
    ).count()

    return render(request, 'tasks/my_tasks.html', {
        'tasks': tasks,

        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,

        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,

        'total_tasks_count': total_tasks_count,
        'active_tasks_count': active_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'overdue_tasks_count': overdue_tasks_count,

        'today': timezone.localdate(),
    })