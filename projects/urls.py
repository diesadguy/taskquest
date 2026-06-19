from django.urls import path

from . import views


urlpatterns = [
    path('', views.project_list_view, name='project_list'),

    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_update_view, name='project_update'),
    path('projects/<int:project_id>/delete/', views.project_delete_view, name='project_delete'),
    path('projects/<int:project_id>/complete/', views.project_complete_view, name='project_complete'),



    path('projects/<int:project_id>/invite/', views.invite_user_view, name='invite_user'),

    path('invitations/', views.invitation_list_view, name='invitation_list'),
    path('invitations/<int:invitation_id>/accept/', views.accept_invitation_view, name='accept_invitation'),
    path('invitations/<int:invitation_id>/decline/', views.decline_invitation_view, name='decline_invitation'),
]