from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views import View
from django.utils import timezone
from datetime import timedelta
from apps.universities.models import University
from apps.accounts.models import User
from .utils import generate_otp, send_2fa_otp_email

class TenantLoginView(View):
    """
    Split-screen, tenant-aware login page.
    Automatically loads branding based on the /login/<slug>/ URL.
    """
    def get(self, request, slug=None):
        if not slug:
            # Render a generic system login if accessed via standard /accounts/login/
            return render(request, 'accounts/login.html', {'university': None})

        university = get_object_or_404(University, slug=slug, is_active=True)
        return render(request, 'accounts/login.html', {'university': university})

    def post(self, request, slug=None):
        university = get_object_or_404(University, slug=slug, is_active=True) if slug else None

        email = request.POST.get('email')
        password = request.POST.get('password')

        # Since we haven't overridden the USERNAME_FIELD model config in our base code yet,
        # we manually retrieve the user by email to ensure `authenticate` works using the default backend.
        user_by_email = User.objects.filter(email=email).first()

        if user_by_email:
            user = authenticate(request, username=user_by_email.username, password=password)
        else:
            user = authenticate(request, username=email, password=password)

        if user is not None:
            if university and user.university != university and not user.is_superuser:
                messages.error(request, "This account does not belong to this institution.")
                return render(request, 'accounts/login.html', {'university': university})

            # Generate OTP for 2FA
            otp = generate_otp()
            # Store temporarily in session
            request.session['2fa_otp'] = otp
            request.session['2fa_user_id'] = str(user.id)
            request.session['2fa_expiry'] = (timezone.now() + timedelta(minutes=10)).timestamp()
            request.session['tenant_slug'] = slug or 'system'

            # Temporarily bypass 2FA for the admin user for initial setup
            if user.username == 'admin':
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                return redirect('user_dashboard')

            send_2fa_otp_email(user, otp)
            return redirect('verify_2fa')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, 'accounts/login.html', {'university': university})

class Verify2FAView(View):
    """
    Verifies the OTP sent to the user's email before finalizing the login.
    """
    def get(self, request):
        if '2fa_user_id' not in request.session:
            return redirect('home')
        return render(request, 'accounts/verify_2fa.html')

    def post(self, request):
        if '2fa_user_id' not in request.session:
            return redirect('home')

        submitted_otp = request.POST.get('otp')
        expected_otp = request.session.get('2fa_otp')
        expiry_timestamp = request.session.get('2fa_expiry')
        user_id = request.session.get('2fa_user_id')

        if not expected_otp or not expiry_timestamp or timezone.now().timestamp() > expiry_timestamp:
            messages.error(request, "Your verification code has expired. Please log in again.")
            request.session.flush()
            return redirect('home')

        if submitted_otp == expected_otp:
            user = User.objects.get(id=user_id)
            auth_login(request, user)
            request.session.pop('2fa_otp', None)
            request.session.pop('2fa_user_id', None)
            request.session.pop('2fa_expiry', None)

            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid verification code.")
            return render(request, 'accounts/verify_2fa.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')
