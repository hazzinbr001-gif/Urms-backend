from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import RedirectView
from apps.dashboards.views import UserDashboardView, AdminDashboardView


def health_check(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    # Root redirect: superusers go to admin dashboard, others to user dashboard
    path('', RedirectView.as_view(pattern_name='user_dashboard', permanent=False), name='home'),

    # Dashboards (both names kept for template compatibility)
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('dashboard/home/', UserDashboardView.as_view(), name='dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),

    # App URL includes
    path('accounts/', include('apps.accounts.urls')),
    path('proposals/', include('apps.proposals.urls')),
    path('audit/', include('apps.audit_logs.urls')),
    path('documents/', include('apps.documents.urls')),
    path('core/', include('core.urls')),
]
