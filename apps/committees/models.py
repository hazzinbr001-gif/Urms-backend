from django.db import models
from core.models import BaseModel
from apps.universities.models import University
from apps.accounts.models import User

class CommitteeType(models.TextChoices):
    DEPARTMENT = 'DEPARTMENT', 'Department Committee'
    SCHOOL = 'SCHOOL', 'School Committee'
    ETHICS = 'ETHICS', 'Ethics Committee'

class Committee(BaseModel):
    name = models.CharField(max_length=255)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='committees')
    type = models.CharField(max_length=50, choices=CommitteeType.choices, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['university', 'type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class CommitteeMember(BaseModel):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='committee_memberships')
    role = models.CharField(max_length=100, help_text="Role within the committee (e.g., Chair, Reviewer)")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('committee', 'user')
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.committee.name}"
