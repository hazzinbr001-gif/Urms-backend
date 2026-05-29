from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from .models import DocumentSection, DocumentSubmission
from apps.proposals.models import Proposal

class DocumentTrackingView(LoginRequiredMixin, ListView):
    template_name = 'documents/tracking.html'
    context_object_name = 'sections'

    def get_queryset(self):
        self.proposal = get_object_or_404(
            Proposal,
            pk=self.kwargs['proposal_id'],
            university=self.request.user.university
        )
        # Fetch sections for this university
        return DocumentSection.objects.filter(university=self.request.user.university).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proposal'] = self.proposal

        # Get latest submissions for each section
        submissions_dict = {}
        for submission in DocumentSubmission.objects.filter(proposal=self.proposal).order_by('section_id', '-version'):
            if submission.section_id not in submissions_dict:
                submissions_dict[submission.section_id] = submission

        context['submissions'] = submissions_dict

        # Progress calculation
        total_sections = self.get_queryset().filter(is_required=True).count()
        approved_sections = sum(1 for s in submissions_dict.values() if s.section.is_required and s.status == 'APPROVED')

        context['progress_percentage'] = int((approved_sections / total_sections * 100) if total_sections > 0 else 0)
        return context

class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = DocumentSubmission
    fields = ['file']
    template_name = 'core/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = get_object_or_404(Proposal, pk=self.kwargs['proposal_id'], university=self.request.user.university)
        section = get_object_or_404(DocumentSection, pk=self.kwargs['section_id'], university=self.request.user.university)
        context['title'] = f"Upload Document: {section.title}"
        context['button_text'] = "Upload"
        return context

    def form_valid(self, form):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['proposal_id'], university=self.request.user.university)
        section = get_object_or_404(DocumentSection, pk=self.kwargs['section_id'], university=self.request.user.university)

        # Calculate version
        latest_version = DocumentSubmission.objects.filter(proposal=proposal, section=section).count()

        form.instance.proposal = proposal
        form.instance.section = section
        form.instance.uploaded_by = self.request.user
        form.instance.version = latest_version + 1
        form.instance.status = 'PENDING'

        messages.success(self.request, f"Document uploaded for section {section.title}.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('documents:tracking', kwargs={'proposal_id': self.kwargs['proposal_id']})

class DocumentReviewView(LoginRequiredMixin, UpdateView):
    model = DocumentSubmission
    fields = ['status', 'supervisor_feedback']
    template_name = 'core/generic_form.html'

    def get_queryset(self):
        return DocumentSubmission.objects.filter(proposal__university=self.request.user.university)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Review Document: {self.object.section.title}"
        context['button_text'] = "Submit Review"
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Document reviewed.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('documents:tracking', kwargs={'proposal_id': self.object.proposal.id})
