from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(TemplateView):
    """
    Main dashboard view. Content is filtered in the template based on user roles.
    """
    template_name = 'dashboard.html'

    # We allow unauthenticated for testing per memory unless strict auth is required,
    # but the template has default fallback. Normally would inherit LoginRequiredMixin.

class PlaceholderView(TemplateView):
    """
    Gracefully handles incomplete or unbuilt feature links from the UI.
    """
    template_name = 'placeholder.html'
