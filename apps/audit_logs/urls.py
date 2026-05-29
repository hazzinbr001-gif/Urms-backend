from django.urls import path
from .views import GovernanceLogsView

urlpatterns = [
    path('logs/', GovernanceLogsView.as_view(), name='governance_logs'),
]
