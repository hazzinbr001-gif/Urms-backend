from django import forms
from apps.universities.models import University
from apps.accounts.models import User

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500 sm:text-sm py-2 px-3 border'

class UniversityForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = University
        fields = ['name', 'slug', 'domain', 'description', 'logo_url', 'background_image_url', 'is_active']

from core.constants import Roles
from .models import UserRole

class AdminUserCreateForm(TailwindFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text="Set an initial password for the user.")
    roles = forms.MultipleChoiceField(choices=Roles.CHOICES, required=False, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'university', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        # Hide university field for non-superusers
        if self.request_user and not self.request_user.is_superuser:
            self.fields.pop('university')

        # Filter roles based on hierarchy power
        if self.request_user and not self.request_user.is_superuser:
            highest_power = max([Roles.HIERARCHY.get(r.role, 0) for r in self.request_user.roles.all()], default=0)
            allowed_choices = [(k, v) for k, v in Roles.CHOICES if Roles.HIERARCHY.get(k, 0) < highest_power]
            self.fields['roles'].choices = allowed_choices

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if self.request_user and not self.request_user.is_superuser:
             user.university = self.request_user.university

        if commit:
            user.save()
            for r in self.cleaned_data['roles']:
                UserRole.objects.create(user=user, role=r)
        return user


class AdminUserUpdateForm(TailwindFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank to keep the current password. Enter a new password to reset it.")
    roles = forms.MultipleChoiceField(choices=Roles.CHOICES, required=False, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'university', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        # Populate initial roles
        if self.instance and self.instance.pk:
            self.fields['roles'].initial = [r.role for r in self.instance.roles.all()]

        # Hide university field for non-superusers
        if self.request_user and not self.request_user.is_superuser:
            self.fields.pop('university')

        # Filter roles based on hierarchy power
        if self.request_user and not self.request_user.is_superuser:
            highest_power = max([Roles.HIERARCHY.get(r.role, 0) for r in self.request_user.roles.all()], default=0)
            allowed_choices = [(k, v) for k, v in Roles.CHOICES if Roles.HIERARCHY.get(k, 0) < highest_power]
            self.fields['roles'].choices = allowed_choices

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Update roles
            UserRole.objects.filter(user=user).delete()
            for r in self.cleaned_data['roles']:
                UserRole.objects.create(user=user, role=r)
        return user
