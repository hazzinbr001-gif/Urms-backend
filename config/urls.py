from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from core.views import DashboardView, PlaceholderView


def health_check(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard_explicit'),
    path('core/placeholder/', PlaceholderView.as_view(), name='placeholder'),
]
