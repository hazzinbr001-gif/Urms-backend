from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class PlaceholderViewTests(TestCase):
    def test_placeholder_renders(self):
        client = Client()
        user = User.objects.create_user(username='test', password='password123')
        client.force_login(user)
        response = client.get(reverse('placeholder') + '?feature=API%20Keys')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/placeholder.html')
        self.assertContains(response, 'API Keys')
