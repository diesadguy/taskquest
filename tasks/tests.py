from django.test import TestCase
from django.contrib.auth.models import User

from projects.models import Project
from .models import Task, Tag, Comment


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser',
            email='taskuser@example.com',
            password='testpassword123'
        )

        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            project_type='personal',
            owner=self.user
        )
        self.project.members.add(self.user)

    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='medium',
            status='todo'
        )

        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.project, self.project)

    def test_task_completed_at_set_when_done(self):
        task = Task.objects.create(
            title='Done Task',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='medium',
            status='done'
        )

        task.mark_completed_if_needed()
        task.save()

        self.assertIsNotNone(task.completed_at)

    def test_task_completed_at_removed_when_not_done(self):
        task = Task.objects.create(
            title='Done Task',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='medium',
            status='done'
        )

        task.mark_completed_if_needed()
        task.save()

        task.status = 'todo'
        task.mark_completed_if_needed()
        task.save()

        self.assertIsNone(task.completed_at)

    def test_tag_creation(self):
        tag = Tag.objects.create(
            name='Backend',
            color='primary',
            project=self.project
        )

        self.assertEqual(tag.name, 'Backend')
        self.assertEqual(tag.project, self.project)

    def test_comment_creation(self):
        task = Task.objects.create(
            title='Task with comment',
            project=self.project,
            assignee=self.user,
            created_by=self.user
        )

        comment = Comment.objects.create(
            task=task,
            author=self.user,
            text='Test comment'
        )

        self.assertEqual(comment.task, task)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, 'Test comment')