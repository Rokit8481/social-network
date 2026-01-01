from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Follow

User = get_user_model()

class UserModelTest(TestCase):

    def test_user_str(self):
        user = User.objects.create_user(username="roman", password="123")
        self.assertEqual(str(user), "roman")

    def test_slug_created(self):
        user = User.objects.create_user(username="roman", password="123")
        self.assertIsNotNone(user.slug)

class FollowModelTest(TestCase):

    def test_unique_follow(self):
        u1 = User.objects.create_user("a", password="123")
        u2 = User.objects.create_user("b", password="123")

        Follow.objects.create(follower=u1, following=u2)

        with self.assertRaises(Exception):
            Follow.objects.create(follower=u1, following=u2)
