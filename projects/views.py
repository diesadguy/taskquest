from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from notifications.models import Notification

from .forms import ProjectForm, ProjectInvitationForm
from .models import Project, ProjectInvitation


@login_required
def project_list_view(request):
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user),
        is_completed=False
    ).distinct()

    completed_projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user),
        is_completed=True
    ).distinct()

    my_tasks = request.user.assigned_tasks.select_related(
        'project',
        'created_by'
    )

    active_tasks = my_tasks.exclude(status='done')

    overdue_tasks = active_tasks.filter(
        deadline__lt=timezone.localdate()
    )

    upcoming_tasks = active_tasks.filter(
        deadline__isnull=False
    ).order_by('deadline')[:5]

    recent_projects = projects[:6]

    projects_count = projects.count()
    active_tasks_count = active_tasks.count()
    overdue_tasks_count = overdue_tasks.count()
    completed_tasks_count = my_tasks.filter(status='done').count()

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'completed_projects': completed_projects,
        'recent_projects': recent_projects,
        'projects_count': projects_count,
        'active_tasks_count': active_tasks_count,
        'overdue_tasks_count': overdue_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'upcoming_tasks': upcoming_tasks,
        'today': timezone.localdate(),
    })


@login_required
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.members.add(request.user)

            messages.success(request, 'Проект успешно создан.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Создание проекта'
    })


@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not project.is_member(request.user):
        messages.error(request, 'У вас нет доступа к этому проекту.')
        return redirect('project_list')

    tasks = project.tasks.all()

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    assignee_filter = request.GET.get('assignee', '')

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    if assignee_filter:
        tasks = tasks.filter(assignee_id=assignee_filter)

    all_tasks = project.tasks.all()
    total_tasks_count = all_tasks.count()
    completed_tasks_count = all_tasks.filter(status='done').count()

    if total_tasks_count > 0:
        progress_percent = int((completed_tasks_count / total_tasks_count) * 100)
    else:
        progress_percent = 0

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assignee_filter': assignee_filter,
        'total_tasks_count': total_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'progress_percent': progress_percent,
        'today': timezone.localdate(),
    })


@login_required
def project_update_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(request, 'Редактировать проект может только владелец.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            messages.success(request, 'Проект успешно обновлён.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Редактирование проекта'
    })


@login_required
def project_delete_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(request, 'Удалить проект может только владелец.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Проект успешно удалён.')
        return redirect('project_list')

    return render(request, 'projects/project_confirm_delete.html', {
        'project': project
    })


@login_required
def invite_user_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(request, 'Приглашать пользователей может только владелец проекта.')
        return redirect('project_detail', project_id=project.id)

    if project.project_type != 'team':
        messages.error(request, 'Приглашения доступны только для командных проектов.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectInvitationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            try:
                invited_user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким username не найден.')
                return redirect('invite_user', project_id=project.id)

            if invited_user == request.user:
                messages.error(request, 'Нельзя пригласить самого себя.')
                return redirect('invite_user', project_id=project.id)

            if project.members.filter(id=invited_user.id).exists():
                messages.error(request, 'Этот пользователь уже является участником проекта.')
                return redirect('invite_user', project_id=project.id)

            invitation, created = ProjectInvitation.objects.get_or_create(
                project=project,
                invited_user=invited_user,
                defaults={
                    'invited_by': request.user,
                    'status': 'pending'
                }
            )

            Notification.objects.create(
                user=invited_user,
                title='Приглашение в проект',
                text=f'Вас пригласили в проект "{project.title}"'
            )

            if not created:
                if invitation.status == 'pending':
                    messages.warning(request, 'Этому пользователю уже отправлено приглашение.')
                elif invitation.status == 'declined':
                    invitation.status = 'pending'
                    invitation.invited_by = request.user
                    invitation.save()
                    messages.success(request, 'Приглашение отправлено повторно.')
                elif invitation.status == 'accepted':
                    messages.info(request, 'Пользователь уже принял приглашение.')
            else:
                messages.success(request, 'Приглашение успешно отправлено.')

            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectInvitationForm()

    return render(request, 'projects/invite_user.html', {
        'form': form,
        'project': project
    })


@login_required
def invitation_list_view(request):
    invitations = ProjectInvitation.objects.filter(
        invited_user=request.user,
        status='pending'
    )

    return render(request, 'projects/invitations.html', {
        'invitations': invitations
    })


@login_required
def accept_invitation_view(request, invitation_id):
    invitation = get_object_or_404(
        ProjectInvitation,
        id=invitation_id,
        invited_user=request.user,
        status='pending'
    )

    if request.method == 'POST':
        invitation.status = 'accepted'
        invitation.save()

        invitation.project.members.add(request.user)

        messages.success(
            request,
            f'Вы присоединились к проекту "{invitation.project.title}".'
        )
        return redirect('project_detail', project_id=invitation.project.id)

    return redirect('invitation_list')


@login_required
def decline_invitation_view(request, invitation_id):
    invitation = get_object_or_404(
        ProjectInvitation,
        id=invitation_id,
        invited_user=request.user,
        status='pending'
    )

    if request.method == 'POST':
        invitation.status = 'declined'
        invitation.save()

        messages.info(
            request,
            f'Вы отклонили приглашение в проект "{invitation.project.title}".'
        )

    return redirect('invitation_list')


@login_required
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        messages.error(
            request,
            'Только владелец проекта может завершить проект.'
        )
        return redirect('project_detail', project_id=project_id)

    project.is_completed = True
    project.completed_at = timezone.now()
    project.save()

    users = list(project.members.all())

    if project.owner not in users:
        users.append(project.owner)

    for user in users:
        Notification.objects.create(
            user=user,
            title='Проект завершён',
            text=f'Проект "{project.title}" был завершён.'
        )

    messages.success(
        request,
        f'Проект"{project.title}"завершен.'
    )

    return redirect('project_list')

