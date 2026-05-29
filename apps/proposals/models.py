from django.db import models
from core.models import BaseModel
from core.constants import WorkflowState
from apps.universities.models import University
from apps.accounts.models import User

class Proposal(BaseModel):
    title = models.CharField(max_length=500, db_index=True)
    abstract = models.TextField()
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='proposals')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_proposals')
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='supervised_proposals'
    )

    # Workflow State tracking, highly queried so it needs an index
    state = models.CharField(
        max_length=50,
        choices=WorkflowState.CHOICES,
        default=WorkflowState.DRAFT,
        db_index=True
    )

    # Metadata for AI analysis and checks
    ai_score = models.FloatField(null=True, blank=True, help_text="AI calculated quality/integrity score")
    plagiarism_score = models.FloatField(null=True, blank=True)

    class Meta:
        # Composite index for tenant-level queries
        indexes = [
            models.Index(fields=['university', 'state']),
            models.Index(fields=['student', 'state']),
        ]

    def __str__(self):
        return f"{self.title} ({self.state})"
