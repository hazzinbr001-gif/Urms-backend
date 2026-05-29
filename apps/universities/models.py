from django.db import models
from core.models import BaseModel, SoftDeleteModel

class University(SoftDeleteModel):
    """
    The core model representing a multi-tenant university in the platform.
    Every other data point in the system must be isolated by this University ID.
    """
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=100, unique=True, help_text="e.g., mit.edu")
    is_active = models.BooleanField(default=True)

    # Theme Configuration
    primary_color = models.CharField(max_length=7, default="#22c55e", help_text="Hex code for primary color")
    secondary_color = models.CharField(max_length=7, default="#16a34a", help_text="Hex code for secondary color")
    logo_url = models.URLField(blank=True, null=True, help_text="URL to the university's logo")

    def __str__(self):
        return self.name
