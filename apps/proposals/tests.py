from django.test import TestCase
from apps.universities.models import University
from apps.accounts.models import User, UserRole
from apps.proposals.models import Proposal
from apps.audit_logs.models import AuditLog
from core.constants import Roles, WorkflowState
from services.proposal_service import ProposalService

class ProposalServiceTest(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University", domain="test.edu")
        self.student = User.objects.create(username="student", university=self.university)
        UserRole.objects.create(user=self.student, role=Roles.STUDENT)

        self.proposal = Proposal.objects.create(
            title="Service Test Proposal",
            abstract="Abstract",
            university=self.university,
            student=self.student,
            state=WorkflowState.DRAFT
        )

    def test_submit_concept(self):
        updated_proposal = ProposalService.submit_concept(self.proposal, self.student)
        self.assertEqual(updated_proposal.state, WorkflowState.CONCEPT_SUBMITTED)

        log = AuditLog.objects.filter(proposal=updated_proposal).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.new_state, WorkflowState.CONCEPT_SUBMITTED)
