from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import AuditLog

class GovernanceLogsView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit_logs/list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.all().select_related('actor', 'proposal').order_by('-created_at')
        elif user.university:
            return AuditLog.objects.filter(proposal__university=user.university).select_related('actor', 'proposal').order_by('-created_at')
        return AuditLog.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Format logs for our standard data_table component
        table_rows = []
        for log in context['logs']:
            # Apply Enterprise Privacy Controls
            is_anonymized = False
            user = self.request.user
            if user.is_superuser and log.proposal and log.proposal.university and not log.proposal.university.share_logs_with_superuser:
                is_anonymized = True

            if is_anonymized:
                actor_name = f"Anonymized ({log.proposal.university.name})"
                proposal_title = "Anonymized Proposal Data"
                role_label = "Redacted"
            else:
                actor_name = log.actor.username if log.actor else "System"
                proposal_title = log.proposal.title[:30] + "..." if log.proposal and len(log.proposal.title) > 30 else (log.proposal.title if log.proposal else "N/A")
                role_label = log.role or "N/A"

            # Highlight state transitions
            transition = f"<span class='text-gray-500 line-through mr-1'>{log.previous_state}</span> <i class='fa-solid fa-arrow-right text-xs mx-1'></i> <span class='font-medium text-gray-900'>{log.new_state}</span>"

            row_data = {
                'cells': [
                    log.created_at.strftime("%Y-%m-%d %H:%M"),
                    actor_name,
                    role_label,
                    proposal_title
                ],
                'raw_html_cell': transition
            }
            table_rows.append(row_data)

        context['table_headers'] = ['Timestamp', 'Actor', 'Role', 'Proposal', 'State Transition']
        context['table_rows'] = table_rows
        return context
