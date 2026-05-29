import json
import logging
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import connection
from django.db.utils import OperationalError
from core.constants import Roles, WorkflowState
from apps.accounts.models import User
from apps.universities.models import University
from apps.proposals.models import Proposal

logger = logging.getLogger(__name__)

class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    Unified dashboard for regular users (Researchers, Supervisors, Dept Heads).
    Dynamically loads context based on their assigned roles.
    """
    template_name = 'dashboards/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine primary role for UI adaptation
        roles = user.roles.values_list('role', flat=True) if user.is_authenticated and hasattr(user, 'roles') else []

        # In a real app, query actual models here
        # Real backend aggregates for user dashboard
        proposals_qs = Proposal.objects.filter(university=user.university)
        if Roles.STUDENT in roles:
            proposals_qs = proposals_qs.filter(student=user)

        drafts = proposals_qs.filter(state=WorkflowState.DRAFT).count()
        approved = proposals_qs.filter(state=WorkflowState.APPROVED).count()
        pending = proposals_qs.exclude(state__in=[WorkflowState.DRAFT, WorkflowState.APPROVED, WorkflowState.REJECTED]).count()

        context['stat_cards'] = [
            {'title': 'Draft Proposals', 'value': drafts, 'icon_class': 'fa-regular fa-file-lines', 'icon_color': 'text-gray-500'},
            {'title': 'Pending Reviews', 'value': pending, 'icon_class': 'fa-solid fa-clock-rotate-left', 'icon_color': 'text-yellow-500'},
            {'title': 'Approved', 'value': approved, 'icon_class': 'fa-solid fa-check-circle', 'icon_color': 'text-green-500'}
        ]

        from django.urls import reverse
        context['quick_actions'] = [
            {'title': 'New Proposal', 'desc': 'Start a new research concept', 'icon': 'fa-solid fa-plus', 'url': reverse('create_proposal')},
            {'title': 'My Tasks', 'desc': 'View items requiring your action', 'icon': 'fa-solid fa-list-check', 'url': reverse('proposal_list')},
            {'title': 'Guidelines', 'desc': 'Read university research policies', 'icon': 'fa-solid fa-book-open', 'url': reverse('placeholder') + '?feature=Guidelines'},
        ]

        context['recent_activities'] = [
            {'description': 'Your proposal <b>"AI in Healthcare"</b> was approved by supervisor.', 'time_ago': '2 hours ago', 'icon': 'fa-solid fa-check', 'color': 'green'},
            {'description': 'New comment on <b>"Quantum Computing"</b> from reviewer.', 'time_ago': '1 day ago', 'icon': 'fa-regular fa-comment', 'color': 'blue'},
        ]

        # Sample Chart.js Configuration
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Proposals Submitted',
                    'data': [1, 2, 0, 3, 1, 4],
                    'backgroundColor': 'rgba(34, 197, 94, 0.5)', # brand-500 with opacity
                    'borderColor': 'rgb(22, 163, 74)', # brand-600
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {'y': {'beginAtZero': True}}
            }
        }
        context['chart_config'] = json.dumps(chart_config)

        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Dedicated dashboard for Superusers or University Admins.
    Provides system-wide or tenant-wide metrics and health.
    """
    template_name = 'dashboards/admin_dashboard.html'

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'roles') and user.roles.filter(role=Roles.RESEARCH_OFFICE_ADMIN).exists():
            return True
        return False

    def check_db_health(self):
        try:
            connection.ensure_connection()
            return 'OK'
        except OperationalError:
            return 'ERROR'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from django.urls import reverse
        from apps.audit_logs.models import AuditLog

        # Branch logic: Superuser vs Tenant Admin
        if user.is_superuser:
            # GLOBAL STATS
            total_users = User.objects.filter(is_active=True).count()
            total_proposals = Proposal.objects.count()
            total_universities = University.objects.filter(is_active=True).count()

            context['stat_cards'] = [
                {'title': 'Total Active Users', 'value': total_users, 'icon_class': 'fa-solid fa-users', 'icon_color': 'text-blue-500'},
                {'title': 'Active Proposals', 'value': total_proposals, 'icon_class': 'fa-solid fa-folder-open', 'icon_color': 'text-brand-500'},
                {'title': 'Onboarded Universities', 'value': total_universities, 'icon_class': 'fa-solid fa-building-columns', 'icon_color': 'text-purple-500'},
                {'title': 'System Status', 'value': 'Online', 'icon_class': 'fa-solid fa-server', 'icon_color': 'text-green-500'}
            ]

            # TENANT TABLE
            universities = University.objects.filter(is_active=True).order_by('-created_at')[:5]
            table_rows = []
            for uni in universities:
                users_count = uni.users.count()
                proposals_count = uni.proposals.count()
                status_badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>'
                table_rows.append({
                    'cells': [uni.name, uni.domain, users_count, proposals_count],
                    'status_badge': status_badge
                })
            context['data_table_title'] = "Recently Onboarded Tenants"
            context['table_headers'] = ['University Name', 'Domain', 'Users', 'Proposals', 'Status']
            context['table_rows'] = table_rows
            context['table_action_btn_text'] = "View All"
            context['table_action_btn_url'] = reverse('manage_universities')

            # QUICK ACTIONS (Global)
            context['quick_actions'] = [
                {'title': 'Global Broadcast', 'desc': 'Send an alert to all tenants', 'icon': 'fa-solid fa-bullhorn', 'url': reverse('placeholder') + "?feature=Global%20Broadcast"},
                {'title': 'Manage Tenants', 'desc': 'Add or suspend Universities', 'icon': 'fa-solid fa-building-columns', 'url': reverse('manage_universities')},
                {'title': 'Security Logs', 'desc': 'Review advanced system audit logs', 'icon': 'fa-solid fa-shield-halved', 'url': reverse('governance_logs')},
            ]

            # AUDIT LOGS (Global)
            recent_logs = AuditLog.objects.all().select_related('actor', 'proposal', 'proposal__university').order_by('-created_at')[:5]

        else:
            # TENANT ADMIN STATS (Scoped)
            tenant = user.university
            total_users = User.objects.filter(university=tenant, is_active=True).count()
            total_proposals = Proposal.objects.filter(university=tenant).count()

            context['stat_cards'] = [
                {'title': 'Tenant Users', 'value': total_users, 'icon_class': 'fa-solid fa-users', 'icon_color': 'text-blue-500'},
                {'title': 'Tenant Proposals', 'value': total_proposals, 'icon_class': 'fa-solid fa-folder-open', 'icon_color': 'text-brand-500'},
                {'title': 'Subscription Status', 'value': 'Active', 'icon_class': 'fa-solid fa-file-contract', 'icon_color': 'text-green-500'},
            ]

            # USER TABLE (Scoped)
            recent_users = User.objects.filter(university=tenant).order_by('-date_joined')[:5]
            table_rows = []
            for u in recent_users:
                status_badge = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>' if u.is_active else '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Suspended</span>'
                table_rows.append({
                    'cells': [u.username, u.email, u.date_joined.strftime("%Y-%m-%d")],
                    'status_badge': status_badge
                })
            context['data_table_title'] = "Recently Joined Users"
            context['table_headers'] = ['Username', 'Email', 'Joined', 'Status']
            context['table_rows'] = table_rows
            context['table_action_btn_text'] = "Manage Users"
            context['table_action_btn_url'] = reverse('manage_users')

            # QUICK ACTIONS (Scoped)
            context['quick_actions'] = [
                {'title': 'Manage Users', 'desc': 'Add or edit user accounts', 'icon': 'fa-solid fa-users-gear', 'url': reverse('manage_users')},
                {'title': 'Institution Settings', 'desc': 'Configure workspace', 'icon': 'fa-solid fa-gear', 'url': reverse('placeholder') + "?feature=Institution%20Settings"},
                {'title': 'Governance Logs', 'desc': 'Review tenant activity', 'icon': 'fa-solid fa-shield-halved', 'url': reverse('governance_logs')},
            ]

            # AUDIT LOGS (Scoped)
            recent_logs = AuditLog.objects.filter(proposal__university=tenant).select_related('actor', 'proposal').order_by('-created_at')[:5]

        # System Health Metrics (Rendered for both currently, could be hidden for tenant admins if desired)
        context['db_status'] = self.check_db_health()
        context['cache_status'] = 'OK'
        context['worker_status'] = 'OK'

        # Format Real Audit Logs for Template
        from django.utils.html import format_html, escape
        formatted_activities = []
        for log in recent_logs:
            # Privacy Control: Anonymize if superuser and tenant disabled sharing
            if user.is_superuser and log.proposal and log.proposal.university and not log.proposal.university.share_logs_with_superuser:
                desc = format_html("Anonymized action occurred in {}.", log.proposal.university.name)
            else:
                actor_name = log.actor.username if log.actor else "System"
                proposal_title = log.proposal.title[:15] + "..." if log.proposal and len(log.proposal.title) > 15 else (log.proposal.title if log.proposal else "N/A")
                desc = format_html("<b>{}</b> transitioned proposal '{}' to {}.", actor_name, proposal_title, log.new_state)

            icon = 'fa-solid fa-check' if 'APPROVE' in log.new_state else ('fa-solid fa-ban' if 'REJECT' in log.new_state else 'fa-solid fa-arrow-right')
            color = 'green' if 'APPROVE' in log.new_state else ('red' if 'REJECT' in log.new_state else 'blue')

            formatted_activities.append({
                'description': desc,
                'time_ago': log.created_at.strftime("%b %d, %H:%M"),
                'icon': icon,
                'color': color
            })

        context['recent_activities'] = formatted_activities if formatted_activities else [{'description': 'No recent logs found.', 'time_ago': '', 'icon': 'fa-regular fa-clock', 'color': 'gray'}]

        # System Load Chart Mock
        chart_config = {
            'type': 'line',
            'data': {
                'labels': ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                'datasets': [{
                    'label': 'API Requests / min',
                    'data': [120, 80, 450, 800, 600, 300, 150],
                    'borderColor': 'rgb(59, 130, 246)', # blue-500
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'fill': True,
                    'tension': 0.4
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': { 'display': False }
                }
            }
        }
        context['chart_config'] = json.dumps(chart_config)

        return context
