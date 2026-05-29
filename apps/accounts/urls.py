from django.urls import path
from .views import TenantLoginView, Verify2FAView, logout_view
from .management_views import (
    UniversityManagementView, UserManagementView,
    UniversityCreateView, UniversityUpdateView,
    UserCreateView, UserUpdateView
)

urlpatterns = [
    # Remove the generic login override. For proper tenant tracking, standard accounts framework endpoints should be used or disabled.
    # The existing path mapping to `login/<slug:slug>/` was failing because the internal `reverse('login')` call in `LoginRequiredMixin` goes to `/accounts/login/` (without a slug).

    path('login/', TenantLoginView.as_view(), name='login'), # Added to fix broken fallback routing
    path('login/<slug:slug>/', TenantLoginView.as_view(), name='tenant_login'),
    path('verify-2fa/', Verify2FAView.as_view(), name='verify_2fa'),
    path('logout/', logout_view, name='logout'),

    # Account Management
    path('manage-universities/', UniversityManagementView.as_view(), name='manage_universities'),
    path('manage-universities/add/', UniversityCreateView.as_view(), name='add_university'),
    path('manage-universities/<uuid:pk>/edit/', UniversityUpdateView.as_view(), name='edit_university'),

    path('manage-users/', UserManagementView.as_view(), name='manage_users'),
    path('manage-users/add/', UserCreateView.as_view(), name='add_user'),
    path('manage-users/<uuid:pk>/edit/', UserUpdateView.as_view(), name='edit_user'),
]
