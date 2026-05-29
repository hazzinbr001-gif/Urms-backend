from django import forms
from .models import Proposal
from apps.accounts.forms import TailwindFormMixin

class ProposalForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'abstract']
        widgets = {
            'abstract': forms.Textarea(attrs={'rows': 5}),
        }
