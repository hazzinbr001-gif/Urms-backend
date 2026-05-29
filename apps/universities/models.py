from django.db import models
from django.utils.text import slugify
from core.models import SoftDeleteModel


class University(SoftDeleteModel):
    """
    The core model representing a multi-tenant university in the platform.
    Every other data point in the system must be isolated by this University ID.
    """
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=100, unique=True, help_text="e.g., mit.edu")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Branding
    description = models.TextField(blank=True, help_text="Short description shown on the login page")
    primary_color = models.CharField(max_length=7, default="#22c55e")
    secondary_color = models.CharField(max_length=7, default="#16a34a")
    logo_url = models.URLField(blank=True, null=True)
    background_image_url = models.URLField(blank=True, null=True, help_text="Hero image on the tenant login page")

    # Governance
    share_logs_with_superuser = models.BooleanField(
        default=True,
        help_text="Allow platform superadmins to see this tenant's audit logs"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
