from django.test import TestCase
from django.urls import reverse
from accounts.models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersListViewTest(TestCase):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("users_list"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_access(self):
        user = User.objects.create_user("u", password="123")
        self.client.login(username="u", password="123")

        response = self.client.get(reverse("users_list"))
        self.assertEqual(response.status_code, 200)

class UserDetailViewTest(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user("a", password="123")
        self.u2 = User.objects.create_user("b", password="123")
        self.client.login(username="a", password="123")

    def test_user_detail_page(self):
        response = self.client.get(
            reverse("user_detail", args=[self.u2.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("is_following", response.context)

class EditUserViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("roman", password="123")
        self.client.login(username="roman", password="123")

    def test_edit_profile(self):
        response = self.client.post(
            reverse("edit_user", args=[self.user.slug]),
            {
                "first_name": "Roman",
                "last_name": "Dev",
                "email": "r@r.com",
                "mobile": "+380501234567"
            }
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Roman")

class ChangePasswordTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("u", password="old123")
        self.client.login(username="u", password="old123")

    def test_change_password(self):
        self.client.post(
            reverse("change_password", args=[self.user.slug]),
            {
                "old_password": "old123",
                "new_password1": "new12345",
                "new_password2": "new12345",
            }
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new12345"))

class ToggleFollowTest(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user("a", password="123")
        self.u2 = User.objects.create_user("b", password="123")
        self.client.login(username="a", password="123")

    def test_toggle_follow(self):
        url = reverse("toggle_follow", args=[self.u2.slug])

        self.client.post(url)
        self.assertEqual(Follow.objects.count(), 1)

        self.client.post(url)
        self.assertEqual(Follow.objects.count(), 0)
