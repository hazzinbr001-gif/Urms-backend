from django.test import TestCase
from apps.universities.models import University
from apps.accounts.models import User, UserRole
from core.constants import Roles

class AccountModelsTest(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University", domain="test.edu")
        self.user = User.objects.create(username="testuser", email="test@test.edu", university=self.university)
        self.user_role = UserRole.objects.create(user=self.user, role=Roles.STUDENT)

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.university.name, "Test University")
        self.assertTrue(hasattr(self.user, "id")) # Has UUID

    def test_user_role(self):
        self.assertEqual(self.user_role.role, Roles.STUDENT)
