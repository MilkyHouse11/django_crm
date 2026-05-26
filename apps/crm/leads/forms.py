from django import forms
from .models import Lead
from .enums import LeadStatus
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class SetAssignedToMixin:
    """Sets "assigned_to" queryset depends on user permissions"""

    action = 'add'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        assigned_to = User.objects.filter(role__name='manager'
                                          ).prefetch_related('membership')

        self.fields['assigned_to'].queryset = assigned_to

        if self.user.has_perm(f'leads.team_{self.action}_lead'):
            self.fields['assigned_to'].queryset = assigned_to.filter(
            membership__team=self.user.membership.team)
        elif self.user.has_perm(f'leads.local_{self.action}_lead'):
            del self.fields['assigned_to']


class CreateLeadForm(SetAssignedToMixin, forms.ModelForm):
    class Meta:
        model = Lead
        exclude = ['created_by', 'status', 'team', 'is_active']


class UpdateLeadForm(SetAssignedToMixin, forms.ModelForm):
    action = 'change'

    class Meta:
        model = Lead
        exclude = ['created_by', 'team']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.user.role.name == 'operator':
            del self.fields['status']

    def clean(self):
        data = super().clean()
        if self.user.role.name == 'manager':
            if self.instance.status != LeadStatus.NEW and data.get('status') == LeadStatus.NEW:
                self.add_error('status', 'Once changed, the lead status cannot be reverted back to "new".')