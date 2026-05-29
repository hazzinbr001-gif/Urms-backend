from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword123')

    def test_user_dashboard_requires_login(self):
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects to login

    def test_user_dashboard_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboards/user_dashboard.html')
        self.assertIn('stat_cards', response.context)
        self.assertIn('chart_config', response.context)

    def test_admin_dashboard_requires_admin(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403) # Forbidden for normal user

    def test_admin_dashboard_authenticated_admin(self):
        self.client.login(username='admin', password='adminpassword123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboards/admin_dashboard.html')
        self.assertIn('stat_cards', response.context)
