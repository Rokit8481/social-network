from django.test import TestCase
from accounts.forms import CustomUserCreationForm


class RegisterFormTest(TestCase):

    def test_valid_form(self):
        form = CustomUserCreationForm(data={
            "username": "roman",
            "mobile": "+380501234567",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        })
        self.assertTrue(form.is_valid())
