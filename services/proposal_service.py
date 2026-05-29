from django.db import transaction
from apps.proposals.models import Proposal
from apps.accounts.models import User
from workflows.state_machine import WorkflowEngine
from core.constants import WorkflowState

class ProposalService:
    """
    Centralized service layer for Proposal business logic.
    Ensures views remain thin and workflow integrity is maintained.
    """

    @staticmethod
    @transaction.atomic
    def submit_concept(proposal: Proposal, user: User) -> Proposal:
        """
        Submits a draft proposal to the department for review.
        """
        WorkflowEngine.transition(proposal, WorkflowState.CONCEPT_SUBMITTED, user, reason="Submitted for initial concept review")
        return proposal

    @staticmethod
    @transaction.atomic
    def assign_supervisor(proposal: Proposal, supervisor: User, assigned_by: User) -> Proposal:
        """
        Assigns a supervisor to an approved concept.
        """
        WorkflowEngine.transition(proposal, WorkflowState.SUPERVISOR_ASSIGNED, assigned_by, reason=f"Assigned supervisor {supervisor.username}")
        proposal.supervisor = supervisor
        proposal.save(update_fields=['supervisor', 'updated_at'])
        return proposal

    @staticmethod
    @transaction.atomic
    def approve_department(proposal: Proposal, user: User, reason: str = "") -> Proposal:
        WorkflowEngine.transition(proposal, WorkflowState.DEPARTMENT_APPROVED, user, reason=reason)
        return proposal

    @staticmethod
    @transaction.atomic
    def reject_proposal(proposal: Proposal, user: User, reason: str) -> Proposal:
        WorkflowEngine.transition(proposal, WorkflowState.REJECTED, user, reason=reason)
        return proposal
