from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from apps.universities.models import University
from .forms import UniversityForm, AdminUserCreateForm, AdminUserUpdateForm
from apps.accounts.models import User, UserRole
from core.constants import Roles

class UniversityManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Superuser-only view for managing multi-tenant Universities.
    """
    template_name = 'accounts/university_management.html'

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        uni_id = request.POST.get('uni_id')

        if action == 'toggle_status' and uni_id:
            uni = University.objects.filter(id=uni_id).first()
            if uni:
                uni.is_active = not uni.is_active
                uni.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        universities = University.objects.all().order_by('-created_at')
        table_rows = []
        for uni in universities:
            users_count = uni.users.count()
            status_badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>' if uni.is_active else '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Suspended</span>'

            row_data = {
                'cells': [uni.name, uni.slug, users_count],
                'status_badge': status_badge,
                'actions': {
                    'type': 'university',
                    'can_edit': True,
                    'edit_url': reverse('edit_university', args=[uni.id]),
                    'can_toggle': True,
                    'is_active': uni.is_active,
                    'id_field': 'uni_id',
                    'id_value': uni.id
                }
            }
            table_rows.append(row_data)

        context['table_headers'] = ['University Name', 'Login Slug', 'Users', 'Status', 'Actions']
        context['table_rows'] = table_rows

        context['quick_actions'] = [
            {'title': 'Add New University', 'desc': 'Onboard a new tenant to the platform', 'icon': 'fa-solid fa-plus', 'url': reverse('add_university')},
            {'title': 'Global API Keys', 'desc': 'Manage integration tokens', 'icon': 'fa-solid fa-key', 'url': reverse('placeholder') + "?feature=API%20Keys"},
        ]
        return context

class UniversityCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = University
    form_class = UniversityForm
    template_name = 'core/generic_form.html'
    success_url = reverse_lazy('manage_universities')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Onboard New University'
        context['description'] = 'Create a new tenant workspace.'
        context['cancel_url'] = self.success_url
        return context

class UniversityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = University
    form_class = UniversityForm
    template_name = 'core/generic_form.html'
    success_url = reverse_lazy('manage_universities')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.object.name}'
        context['cancel_url'] = self.success_url
        return context

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = AdminUserCreateForm
    template_name = 'core/generic_form.html'
    success_url = reverse_lazy('manage_users')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm('accounts.add_user')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            form.instance.university = self.request.user.university
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invite New User'
        context['cancel_url'] = self.success_url
        return context

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = AdminUserUpdateForm
    template_name = 'core/generic_form.html'
    success_url = reverse_lazy('manage_users')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm('accounts.change_user')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(university=self.request.user.university)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.username}'
        context['cancel_url'] = self.success_url
        return context

class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    University Admin view for managing users within their specific tenant,
    enforcing top-down role hierarchy.
    """
    template_name = 'accounts/user_management.html'

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        # Allow anyone with a role value >= 50 (HOD and above can manage SOME users below them)
        if hasattr(user, 'roles'):
            highest_role_val = max([Roles.HIERARCHY.get(r.role, 0) for r in user.roles.all()], default=0)
            return highest_role_val >= Roles.HIERARCHY[Roles.HOD]
        return False

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        target_user_id = request.POST.get('user_id')

        if action == 'toggle_status' and target_user_id:
            target_user = User.objects.filter(id=target_user_id).first()
            if target_user:
                # Re-verify hierarchy before applying changes
                current_user = request.user

                # Explicitly check for granular suspend permission
                if not current_user.is_superuser and not current_user.has_perm('accounts.suspend_user'):
                    return self.get(request, *args, **kwargs)

                if current_user.is_superuser:
                    highest_power = 100
                else:
                    highest_power = max([Roles.HIERARCHY.get(r.role, 0) for r in current_user.roles.all()], default=0)

                target_highest = max([Roles.HIERARCHY.get(r.role, 0) for r in target_user.roles.all()], default=0)

                # Cannot modify superusers, and must be strictly higher in hierarchy
                if not target_user.is_superuser and highest_power > target_highest:
                    # Enforce tenant isolation
                    if current_user.is_superuser or current_user.university == target_user.university:
                        target_user.is_active = not target_user.is_active
                        target_user.save()

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine explicit granular permissions
        can_add = user.is_superuser or user.has_perm('accounts.add_user')
        can_edit_global = user.is_superuser or user.has_perm('accounts.change_user')
        can_suspend_global = user.is_superuser or user.has_perm('accounts.suspend_user')

        # Determine highest role for hierarchy checking
        if user.is_superuser:
            highest_power = 100
            target_university = University.objects.first() # Or let superuser select tenant
            users = User.objects.all().order_by('-date_joined')
        else:
            highest_power = max([Roles.HIERARCHY.get(r.role, 0) for r in user.roles.all()], default=0)
            target_university = user.university
            users = User.objects.filter(university=target_university).order_by('-date_joined')

        table_rows = []
        for u in users:
            roles_list = ", ".join([r.role for r in u.roles.all()])
            u_highest = max([Roles.HIERARCHY.get(r.role, 0) for r in u.roles.all()], default=0)

            status_badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>' if u.is_active else '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Suspended</span>'

            row_data = {
                'cells': [u.username, u.email, roles_list or "No Role"],
                'status_badge': status_badge,
            }

            # Enforce explicit permissions AND strict hierarchy outranking
            has_hierarchy_power = (highest_power > u_highest) and not u.is_superuser

            if has_hierarchy_power and (can_edit_global or can_suspend_global):
                row_data['actions'] = {
                    'type': 'user',
                    'can_edit': can_edit_global,
                    'edit_url': reverse('edit_user', args=[u.id]) if can_edit_global else '#',
                    'can_toggle': can_suspend_global,
                    'is_active': u.is_active,
                    'id_field': 'user_id',
                    'id_value': u.id
                }
            else:
                 row_data['no_actions_message'] = 'Insufficient privileges'

            table_rows.append(row_data)

        context['table_headers'] = ['Username', 'Email', 'Assigned Roles', 'Status', 'Actions']
        context['table_rows'] = table_rows

        # Quick Actions conditionally rendered based on permissions
        context['quick_actions'] = []
        if can_add:
            context['quick_actions'].append({'title': 'Add User', 'desc': 'Invite a new user to the platform', 'icon': 'fa-solid fa-user-plus', 'url': reverse('add_user')})
            context['quick_actions'].append({'title': 'Bulk Import', 'desc': 'Import users via CSV', 'icon': 'fa-solid fa-file-csv', 'url': reverse('placeholder') + "?feature=Bulk%20Import"})
        context['tenant_name'] = target_university.name if target_university else "System Global"
        return context
