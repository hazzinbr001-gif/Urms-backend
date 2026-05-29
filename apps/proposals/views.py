from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Proposal
from .forms import ProposalForm
from workflows.state_machine import WorkflowEngine, WorkflowTransitionError
from core.constants import WorkflowState, Roles

class ProposalCreateView(LoginRequiredMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'core/generic_form.html'
    success_url = reverse_lazy('proposal_list')

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.instance.university = self.request.user.university
        response = super().form_valid(form)

        # Optionally, transition immediately to CONCEPT_SUBMITTED if saving
        # For now, we leave it as DRAFT as per model default
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Proposal Draft'
        context['cancel_url'] = self.success_url
        return context

class ProposalListView(LoginRequiredMixin, ListView):
    model = Proposal
    template_name = 'proposals/list.html'
    context_object_name = 'proposals'

    def get_queryset(self):
        user = self.request.user
        qs = Proposal.objects.filter(university=user.university).order_by('-created_at')

        roles = [r.role for r in getattr(user, 'roles').all()] if hasattr(user, 'roles') else []

        if user.is_superuser:
            return Proposal.objects.all().order_by('-created_at')

        # Role-based query filtering (The Inbox logic)
        if Roles.STUDENT in roles:
            return qs.filter(student=user)

        # Build an OR query based on roles. A user might have multiple roles.
        # For simplicity, we filter by states relevant to the user's highest capabilities.
        visible_states = []
        if Roles.SUPERVISOR in roles:
            return qs.filter(supervisor=user) # Supervisors only see what's assigned to them

        if Roles.DEPARTMENT_COMMITTEE in roles or Roles.HOD in roles:
            visible_states.extend([WorkflowState.CONCEPT_SUBMITTED, WorkflowState.DEPARTMENT_REVIEW, WorkflowState.DEPARTMENT_APPROVED, WorkflowState.SUPERVISOR_ASSIGNED])

        if Roles.SCHOOL_COMMITTEE in roles:
            visible_states.extend([WorkflowState.PROPOSAL_SUBMITTED, WorkflowState.SCHOOL_REVIEW, WorkflowState.SCHOOL_APPROVED])

        if Roles.ETHICS_COMMITTEE in roles:
            visible_states.extend([WorkflowState.SCHOOL_APPROVED, WorkflowState.ETHICS_REVIEW, WorkflowState.ETHICS_APPROVED])

        if Roles.RESEARCH_OFFICE_ADMIN in roles:
            visible_states.extend([WorkflowState.ETHICS_APPROVED, WorkflowState.RESEARCH_REGISTERED, WorkflowState.EXTERNAL_REVIEW, WorkflowState.APPROVED])

        if visible_states:
            return qs.filter(state__in=visible_states)

        # Fallback
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table_rows = []
        for prop in context['proposals']:
            student_name = prop.student.get_full_name() or prop.student.username

            # Action button links to Detail view
            actions = f'<a href="{reverse("proposal_detail", args=[prop.id])}" class="text-brand-600 hover:text-brand-900 font-medium text-sm">Review <i class="fa-solid fa-arrow-right ml-1"></i></a>'

            # Badge color mapping
            badge_color = "gray"
            if prop.state == WorkflowState.APPROVED: badge_color = "green"
            elif prop.state == WorkflowState.REJECTED: badge_color = "red"
            elif prop.state in [WorkflowState.DRAFT]: badge_color = "gray"
            else: badge_color = "blue"

            status_badge = f'<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{badge_color}-100 text-{badge_color}-800">{prop.get_state_display()}</span>'

            table_rows.append({
                'cells': [prop.title, student_name, prop.created_at.strftime("%Y-%m-%d")],
                'status_badge': status_badge,
                'raw_html_cell': actions
            })

        context['table_headers'] = ['Title', 'Student', 'Submitted On', 'Status', 'Action']
        context['table_rows'] = table_rows

        roles = [r.role for r in getattr(self.request.user, 'roles').all()] if hasattr(self.request.user, 'roles') else []
        if Roles.STUDENT in roles:
            context['quick_actions'] = [{'title': 'New Draft', 'desc': 'Start a new concept', 'icon': 'fa-solid fa-plus', 'url': reverse('create_proposal')}]

        return context

from apps.ai_engine.services import AIEngineService
from apps.integrity_engine.services import IntegrityService

class ProposalDetailView(LoginRequiredMixin, DetailView):
    model = Proposal
    template_name = 'proposals/detail.html'
    context_object_name = 'proposal'

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_superuser:
            return qs
        return qs.filter(university=user.university)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object
        user = self.request.user

        # Determine valid transitions for the current user
        user_roles = [ur.role for ur in user.roles.all()]
        available_transitions = []
        for target_state in WorkflowEngine.TRANSITIONS.get(proposal.state, []):
            if WorkflowEngine.is_authorized(user_roles, target_state) or user.is_superuser:
                # Provide human readable labels
                available_transitions.append({
                    'state': target_state,
                    'label': dict(WorkflowState.CHOICES).get(target_state, target_state)
                })

        context['available_transitions'] = available_transitions

        # Inject Mock AI Services Data (Simulating Enterprise Integrity Checking)
        if proposal.state not in [WorkflowState.DRAFT, WorkflowState.CONCEPT_SUBMITTED]:
            # Provide AI Insights to reviewers automatically
            context['ai_score'] = AIEngineService.score_proposal(proposal.id)
            context['ai_critique'] = AIEngineService.critique_proposal(proposal.id)
            context['plagiarism_report'] = IntegrityService.check_plagiarism(proposal.id)
            context['ai_content_report'] = IntegrityService.detect_ai_content(proposal.id)

        # Audit Trail (History)
        context['audit_logs'] = proposal.audit_logs.all().order_by('-created_at')

        return context

class ProposalTransitionView(LoginRequiredMixin, View):
    """
    Handles POST requests for executing a state transition.
    """
    def post(self, request, pk):
        user = request.user
        qs = Proposal.objects.all() if user.is_superuser else Proposal.objects.filter(university=user.university)
        proposal = get_object_or_404(qs, pk=pk)
        target_state = request.POST.get('target_state')
        reason = request.POST.get('reason', '')

        try:
            WorkflowEngine.transition(proposal, target_state, request.user, reason)
            messages.success(request, f"Proposal successfully transitioned to {dict(WorkflowState.CHOICES).get(target_state)}.")
        except WorkflowTransitionError as e:
            messages.error(request, f"Transition failed: {str(e)}")

        return redirect('proposal_detail', pk=proposal.id)
