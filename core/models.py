import uuid
from django.db import models

class UUIDMixin(models.Model):
    """
    Replaces Django's default AutoField ID with a universally unique identifier (UUID).
    Essential for multi-tenant applications and scalable distributed systems to prevent ID enumeration.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """
    Provides standard created_at and updated_at timestamps.
    Automatically managed by Django via auto_now_add and auto_now.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, TimestampMixin):
    """
    The abstract base model to be used by all domain models across the URMS platform.
    Ensures that every entity has a secure UUID and tracking timestamps by default.
    """
    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted objects by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(BaseModel):
    """
    Abstract model extending BaseModel to add soft-delete capabilities.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft deletes the object by setting is_deleted=True and populating deleted_at.
        """
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """
        Restores a soft-deleted object.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class SystemIssueReport(BaseModel):
    """
    Model for capturing bug reports and troubleshooting diagnostic data.
    """
    ROLE_CHOICES = (
        ('SYSTEM_ADMIN', 'System Admin'),
        ('SCHOOL_ADMIN', 'School Admin'),
        ('USER', 'User'),
    )

    reporter_role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER')
    tenant_domain = models.CharField(max_length=100, null=True, blank=True, help_text="The tenant where the issue occurred")
    description = models.TextField(help_text="Detailed description of the issue")
    browser_info = models.TextField(null=True, blank=True, help_text="Diagnostic context (e.g., user agent)")
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Issue Report from {self.tenant_domain or 'Unknown'} - {'Resolved' if self.resolved else 'Pending'}"
