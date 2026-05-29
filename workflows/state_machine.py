from core.constants import WorkflowState, Roles

class WorkflowTransitionError(Exception):
    pass

class WorkflowEngine:
    """
    Centralized State Machine for Proposal Governance.
    Ensures that transitions follow the strict, predefined enterprise workflow.
    """

    TRANSITIONS = {
        WorkflowState.DRAFT: [WorkflowState.CONCEPT_SUBMITTED],
        WorkflowState.CONCEPT_SUBMITTED: [WorkflowState.DEPARTMENT_REVIEW, WorkflowState.REJECTED],
        WorkflowState.DEPARTMENT_REVIEW: [WorkflowState.DEPARTMENT_APPROVED, WorkflowState.REJECTED],
        WorkflowState.DEPARTMENT_APPROVED: [WorkflowState.SUPERVISOR_ASSIGNED],
        WorkflowState.SUPERVISOR_ASSIGNED: [WorkflowState.UNDER_SUPERVISION],
        WorkflowState.UNDER_SUPERVISION: [WorkflowState.PROPOSAL_SUBMITTED],
        WorkflowState.PROPOSAL_SUBMITTED: [WorkflowState.SCHOOL_REVIEW],
        WorkflowState.SCHOOL_REVIEW: [WorkflowState.SCHOOL_APPROVED, WorkflowState.REJECTED],
        WorkflowState.SCHOOL_APPROVED: [WorkflowState.ETHICS_REVIEW],
        WorkflowState.ETHICS_REVIEW: [WorkflowState.ETHICS_APPROVED, WorkflowState.REJECTED],
        WorkflowState.ETHICS_APPROVED: [WorkflowState.RESEARCH_REGISTERED],
        WorkflowState.RESEARCH_REGISTERED: [WorkflowState.EXTERNAL_REVIEW, WorkflowState.APPROVED],
        WorkflowState.EXTERNAL_REVIEW: [WorkflowState.APPROVED, WorkflowState.REJECTED],
        WorkflowState.APPROVED: [],
        WorkflowState.REJECTED: [],
    }

    ROLE_AUTHORIZATION = {
        WorkflowState.CONCEPT_SUBMITTED: [Roles.STUDENT],
        WorkflowState.DEPARTMENT_REVIEW: [Roles.DEPARTMENT_COMMITTEE, Roles.HOD],
        WorkflowState.DEPARTMENT_APPROVED: [Roles.DEPARTMENT_COMMITTEE],
        WorkflowState.SUPERVISOR_ASSIGNED: [Roles.HOD, Roles.DEPARTMENT_COMMITTEE],
        WorkflowState.UNDER_SUPERVISION: [Roles.STUDENT, Roles.SUPERVISOR],
        WorkflowState.PROPOSAL_SUBMITTED: [Roles.STUDENT, Roles.SUPERVISOR],
        WorkflowState.SCHOOL_REVIEW: [Roles.SCHOOL_COMMITTEE],
        WorkflowState.SCHOOL_APPROVED: [Roles.SCHOOL_COMMITTEE],
        WorkflowState.ETHICS_REVIEW: [Roles.ETHICS_COMMITTEE],
        WorkflowState.ETHICS_APPROVED: [Roles.ETHICS_COMMITTEE],
        WorkflowState.RESEARCH_REGISTERED: [Roles.RESEARCH_OFFICE_ADMIN],
        WorkflowState.EXTERNAL_REVIEW: [Roles.RESEARCH_OFFICE_ADMIN],
        WorkflowState.APPROVED: [Roles.RESEARCH_OFFICE_ADMIN, Roles.EXTERNAL_EXAMINER],
        WorkflowState.REJECTED: [
            Roles.DEPARTMENT_COMMITTEE, Roles.SCHOOL_COMMITTEE,
            Roles.ETHICS_COMMITTEE, Roles.RESEARCH_OFFICE_ADMIN
        ],
    }

    @classmethod
    def can_transition(cls, current_state, target_state):
        return target_state in cls.TRANSITIONS.get(current_state, [])

    @classmethod
    def is_authorized(cls, user_roles, target_state):
        allowed_roles = cls.ROLE_AUTHORIZATION.get(target_state, [])
        return any(role in allowed_roles for role in user_roles)

    @classmethod
    def transition(cls, proposal, target_state, user, reason=""):
        from apps.audit_logs.models import AuditLog # Deferred import to avoid circular dependency

        current_state = proposal.state
        user_roles = [ur.role for ur in user.roles.all()]

        if not cls.can_transition(current_state, target_state):
            raise WorkflowTransitionError(f"Invalid transition from {current_state} to {target_state}")

        if not cls.is_authorized(user_roles, target_state):
            raise WorkflowTransitionError(f"User {user.username} is not authorized to transition to {target_state}")

        # Execute Transition
        proposal.state = target_state
        proposal.save()

        # Generate Audit Log automatically
        AuditLog.objects.create(
            proposal=proposal,
            actor=user,
            role=user_roles[0] if user_roles else 'SYSTEM',
            previous_state=current_state,
            new_state=target_state,
            reason=reason
        )
        return True
