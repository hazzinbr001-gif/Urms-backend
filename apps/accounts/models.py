from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from core.models import BaseModel, SoftDeleteModel
from core.constants import Roles
from apps.universities.models import University

from core.models import SoftDeleteManager

class UserManagerWithSoftDelete(SoftDeleteManager, UserManager):
    pass

class User(SoftDeleteModel, AbstractUser):
    """
    Custom User Model overriding Django's default.
    Ensures that every user is linked to a specific university (Multi-tenant requirement).
    """
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="users",
        null=True, blank=True,
        help_text="The tenant this user belongs to. Strictly isolates data."
    )

    objects = UserManagerWithSoftDelete()

    def __str__(self):
        return f"{self.email} - {self.university.name if self.university else 'System'}"

class UserRole(BaseModel):
    """
    RBAC mapping model. A user can have multiple roles within the platform.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=50, choices=Roles.CHOICES)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
