from django.db import models
from core.models import BaseModel
from apps.universities.models import University
from apps.proposals.models import Proposal
from apps.accounts.models import User

class DocumentSection(BaseModel):
    """
    Defines the structural requirements for a proposal (e.g., Chapter 1, Methodology).
    Customizable per University.
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='document_sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ('university', 'title')

    def __str__(self):
        return f"{self.university.name} - {self.title}"

class DocumentSubmission(BaseModel):
    """
    Tracks the actual uploaded file from a student for a specific section,
    including the supervisor's granular approval status.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('REVISION', 'Needs Revision'),
        ('APPROVED', 'Approved'),
    )

    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='documents')
    section = models.ForeignKey(DocumentSection, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    file = models.FileField(upload_to='proposals/documents/%Y/%m/')
    version = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    supervisor_feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['section__order', '-version']

    def __str__(self):
        return f"{self.proposal.title} - {self.section.title} (v{self.version})"
