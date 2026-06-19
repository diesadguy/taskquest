from django.test import TestCase
from django.contrib.auth.models import User

from projects.models import Project
from tasks.models import Task, Comment
from .models import Achievement, UserAchievement, XPLog
from .services import (
    calculate_level,
    reward_task_created,
    reward_task_completed,
    reward_comment_created,
    check_achievements,
)


class GamificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='gameuser',
            email='gameuser@example.com',
            password='testpassword123'
        )

        self.project = Project.objects.create(
            title='Game Project',
            description='Game project description',
            project_type='personal',
            owner=self.user
        )
        self.project.members.add(self.user)

    def test_calculate_level(self):
        self.assertEqual(calculate_level(0), 1)
        self.assertEqual(calculate_level(100), 2)
        self.assertEqual(calculate_level(400), 3)
        self.assertEqual(calculate_level(900), 4)

    def test_reward_task_created_adds_xp(self):
        old_xp = self.user.profile.xp

        reward_task_created(self.user)

        self.user.profile.refresh_from_db()

        self.assertEqual(self.user.profile.xp, old_xp + 10)
        self.assertTrue(
            XPLog.objects.filter(
                user=self.user,
                action='task_created',
                xp_amount=10
            ).exists()
        )

    def test_reward_comment_created_adds_xp(self):
        old_xp = self.user.profile.xp

        reward_comment_created(self.user)

        self.user.profile.refresh_from_db()

        self.assertEqual(self.user.profile.xp, old_xp + 5)

    def test_reward_task_completed_adds_xp(self):
        task = Task.objects.create(
            title='Completed task',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='medium',
            status='done'
        )

        old_xp = self.user.profile.xp

        reward_task_completed(self.user, task)

        self.user.profile.refresh_from_db()

        self.assertEqual(self.user.profile.xp, old_xp + 30)

    def test_high_priority_completed_adds_bonus_xp(self):
        task = Task.objects.create(
            title='High priority task',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='high',
            status='done'
        )

        old_xp = self.user.profile.xp

        reward_task_completed(self.user, task)

        self.user.profile.refresh_from_db()

        self.assertEqual(self.user.profile.xp, old_xp + 50)

    def test_achievement_is_given_once(self):
        Achievement.objects.create(
            title='First task',
            description='Create first task',
            condition_type='tasks_created',
            condition_value=1,
            xp_reward=20
        )

        Task.objects.create(
            title='Created task',
            project=self.project,
            assignee=self.user,
            created_by=self.user,
            priority='medium',
            status='todo'
        )

        check_achievements(self.user)
        check_achievements(self.user)

        achievements_count = UserAchievement.objects.filter(
            user=self.user
        ).count()

        self.assertEqual(achievements_count, 1)

    def test_comment_achievement(self):
        task = Task.objects.create(
            title='Task',
            project=self.project,
            assignee=self.user,
            created_by=self.user
        )

        Achievement.objects.create(
            title='Commentator',
            description='Create one comment',
            condition_type='comments_created',
            condition_value=1,
            xp_reward=10
        )

        Comment.objects.create(
            task=task,
            author=self.user,
            text='Test comment'
        )

        check_achievements(self.user)

        self.assertTrue(
            UserAchievement.objects.filter(
                user=self.user,
                achievement__title='Commentator'
            ).exists()
        )