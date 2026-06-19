from django.test import TestCase
from django.contrib.auth.models import User

from .models import Project, ProjectInvitation


class ProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpassword123'
        )

        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpassword123'
        )

    def test_project_creation(self):
        project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            project_type='personal',
            owner=self.user
        )
        project.members.add(self.user)

        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.owner, self.user)
        self.assertTrue(project.members.filter(id=self.user.id).exists())

    def test_project_list_requires_login(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)

    def test_logged_user_can_create_project(self):
        self.client.login(
            username='owner',
            password='testpassword123'
        )

        response = self.client.post('/projects/create/', {
            'title': 'Created from test',
            'description': 'Description from test',
            'project_type': 'team',
        })

        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(title='Created from test')

        self.assertEqual(project.owner, self.user)
        self.assertTrue(project.members.filter(id=self.user.id).exists())

    def test_project_invitation_accept(self):
        project = Project.objects.create(
            title='Team Project',
            description='Team project description',
            project_type='team',
            owner=self.user
        )
        project.members.add(self.user)

        invitation = ProjectInvitation.objects.create(
            project=project,
            invited_user=self.member,
            invited_by=self.user
        )

        self.client.login(
            username='member',
            password='testpassword123'
        )

        response = self.client.post(
            f'/invitations/{invitation.id}/accept/'
        )

        invitation.refresh_from_db()
        project.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(invitation.status, 'accepted')
        self.assertTrue(project.members.filter(id=self.member.id).exists())