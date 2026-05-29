from django.test import TestCase
from apps.universities.models import University
from apps.accounts.models import User, UserRole
from apps.proposals.models import Proposal
from apps.audit_logs.models import AuditLog
from core.constants import Roles, WorkflowState
from workflows.state_machine import WorkflowEngine, WorkflowTransitionError

class WorkflowEngineTest(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University", domain="test.edu")
        self.student = User.objects.create(username="student", university=self.university)
        self.hod = User.objects.create(username="hod", university=self.university)

        UserRole.objects.create(user=self.student, role=Roles.STUDENT)
        UserRole.objects.create(user=self.hod, role=Roles.HOD)

        self.proposal = Proposal.objects.create(
            title="AI in Healthcare",
            abstract="Research on AI",
            university=self.university,
            student=self.student
        )

    def test_valid_transition(self):
        # Student submits concept
        result = WorkflowEngine.transition(
            proposal=self.proposal,
            target_state=WorkflowState.CONCEPT_SUBMITTED,
            user=self.student,
            reason="Submitting initial concept"
        )
        self.assertTrue(result)
        self.assertEqual(self.proposal.state, WorkflowState.CONCEPT_SUBMITTED)

        # Check Audit Log
        log = AuditLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.new_state, WorkflowState.CONCEPT_SUBMITTED)
        self.assertEqual(log.actor, self.student)
        self.assertEqual(log.reason, "Submitting initial concept")

    def test_invalid_state_transition(self):
        # Draft -> Department Review (Skipping Concept Submitted)
        with self.assertRaises(WorkflowTransitionError):
            WorkflowEngine.transition(self.proposal, WorkflowState.DEPARTMENT_REVIEW, self.student)

    def test_unauthorized_role_transition(self):
        # HOD tries to submit concept (Only Student is allowed)
        with self.assertRaises(WorkflowTransitionError):
            WorkflowEngine.transition(self.proposal, WorkflowState.CONCEPT_SUBMITTED, self.hod)
