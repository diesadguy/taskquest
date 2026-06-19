from django.urls import path

from . import views


urlpatterns = [
    path('my/', views.my_tasks_view, name='my_tasks'),

    path('projects/<int:project_id>/tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),



    path('projects/<int:project_id>/tags/create/', views.tag_create_view, name='tag_create'),

    path('tasks/<int:task_id>/comments/create/', views.comment_create_view, name='comment_create'),
    path('tasks/<int:task_id>/files/upload/', views.file_upload_view, name='file_upload'),

    path('projects/<int:project_id>/kanban/', views.kanban_board_view, name='kanban_board'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status_view, name='update_task_status'),
]

