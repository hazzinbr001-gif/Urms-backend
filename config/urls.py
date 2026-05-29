from django.contrib import admin
from django.urls import path
from core.views import DashboardView, PlaceholderView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Dashboard route
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard_explicit'),

    # Placeholder route for incomplete features
    path('core/placeholder/', PlaceholderView.as_view(), name='placeholder'),
]
