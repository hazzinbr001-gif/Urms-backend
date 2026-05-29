from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.universities.models import University
from apps.proposals.models import Proposal
from .models import AuditLog

class PrivacyPreservingLogsTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Superuser
        self.superuser = User.objects.create_superuser(username='super', password='password123')

        # Tenant that shares logs
        self.uni_open = University.objects.create(name='Open Uni', slug='open', domain='open.edu', share_logs_with_superuser=True)
        self.admin_open = User.objects.create_user(username='admin_open', password='password123', university=self.uni_open)
        self.prop_open = Proposal.objects.create(title='Open Proposal', abstract='...', university=self.uni_open, student=self.admin_open)
        AuditLog.objects.create(proposal=self.prop_open, actor=self.admin_open, previous_state='DRAFT', new_state='SUBMITTED')

        # Tenant that DOES NOT share logs
        self.uni_private = University.objects.create(name='Private Uni', slug='private', domain='private.edu', share_logs_with_superuser=False)
        self.admin_private = User.objects.create_user(username='admin_private', password='password123', university=self.uni_private)
        self.prop_private = Proposal.objects.create(title='Secret Project', abstract='...', university=self.uni_private, student=self.admin_private)
        AuditLog.objects.create(proposal=self.prop_private, actor=self.admin_private, previous_state='DRAFT', new_state='SUBMITTED')

    def test_superuser_sees_anonymized_logs(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('governance_logs'))

        # Should see open proposal details
        self.assertContains(response, 'Open Proposal')
        self.assertContains(response, 'admin_open')

        # Should NOT see private proposal details
        self.assertNotContains(response, 'Secret Project')
        self.assertNotContains(response, 'admin_private')

        # But should see the anonymized placeholder
        self.assertContains(response, 'Anonymized Proposal Data')
        self.assertContains(response, 'Anonymized (Private Uni)')

    def test_tenant_admin_sees_full_logs(self):
        # Even though private uni blocks superusers, its own admins should see everything
        self.client.force_login(self.admin_private)
        response = self.client.get(reverse('governance_logs'))

        self.assertContains(response, 'Secret Project')
        self.assertContains(response, 'admin_private')
        self.assertNotContains(response, 'Anonymized Proposal Data')
