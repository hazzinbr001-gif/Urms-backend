from django.db import models
from core.models import BaseModel
from apps.proposals.models import Proposal
from apps.accounts.models import User

class AuditLog(BaseModel):
    """
    Immutable ledger of every critical action and state transition in the system.
    Fulfills the 'AUDIT LOGGING REQUIREMENTS' for strict enterprise governance.
    """
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='audit_logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_actions')
    role = models.CharField(max_length=100, db_index=True, help_text="The role the user was acting as during this action")

    previous_state = models.CharField(max_length=50)
    new_state = models.CharField(max_length=50, db_index=True)

    reason = models.TextField(blank=True, help_text="Explanation/Comment for the state transition")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['proposal', '-created_at']),
            models.Index(fields=['actor', '-created_at']),
        ]

    def __str__(self):
        return f"{self.proposal.title} | {self.previous_state} -> {self.new_state} by {self.actor.username if self.actor else 'System'}"
