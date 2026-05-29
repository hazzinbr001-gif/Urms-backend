from django import template
from core.constants import Roles

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role_name):
    """
    Checks if a user has a specific role.
    Usage in templates: {% if user|has_role:"STUDENT" %}
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.roles.filter(role=role_name).exists()
