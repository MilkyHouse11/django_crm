from django import forms
from .models import User
from ..teams.models import Team
from ..companies.models import Company
from django.contrib.auth.models import Group


class UserFormMixin:
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.team = kwargs.pop('team', None)
        self.company = kwargs.pop('company', None)
        self.can_change_all_users = kwargs.pop('can_change_all_users', False)
        
        super().__init__(*args, **kwargs)
        
        if not self.can_change_all_users:
            if self.user.has_perm('users.company_change_user'):
                self.fields['role'].queryset = self.fields['role'].queryset.filter(name='team_admin')
            if self.user.has_perm('users.team_change_user'):
                self.fields['role'].queryset = self.fields['role'].queryset.exclude(name__in=['company_admin', 'team_admin'])
        else:
            self.fields['role'].queryset = self.fields['role'].queryset.filter(name='company_admin')
    
    def clean(self):
        data = super().clean()
        
        if self.user.has_perm('users.team_add_user'):
            if not data.get('role'):
                self.add_error('role', 'Role can`t be null')
        
        return data


class UpdateUserForm(UserFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'role']
        
    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password', None)
        
        super().__init__(*args, **kwargs)
        
        if password:
            self.Meta.fields.append('password')

    def clean(self):
        data = super().clean()
        
        if self.can_change_all_users:
            if not self.company:
                self.add_error(None, 'Company can`t be null')
        else:
            if self.team:
                team = Team.objects.filter(id=self.team).first()
                company = self.user.membership.company
                if team and team.company != company:
                    self.add_error(None, 'The team must be from the same company as the user')
        
        return data


class CreateUserForm(UserFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        exclude = ['is_staff', 'is_superuser', 'last_login', 'user_permissions', 'date_joined']
        help_texts = {'role': ''}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
        if self.user.has_perm('users.team_change_user'):
                self.fields['role'].queryset = self.fields['role'].queryset.exclude(
                    name__in=['company_admin', 'team_admin', 'system_admin'])
        else:
            del self.fields['role']
    
    def clean(self):
        data = super().clean()
        
        if self.user.has_perm('users.global_add_user') and not self.company:
            self.add_error(None, "Company can't be null")
        
        if not data.get('first_name') or not data.get('last_name'):
            self.add_error(None, 'Enter first name and last name')
        
        if self.can_change_all_users and self.company and self.team:
            company = Company.objects.filter(id=self.company).first()
            team = Team.objects.filter(id=self.team).first()
            
            if company and team:
                if company != team.company:
                    self.add_error(None, 'The team must be from the same company as the user')
            else:
                self.add_error(None, 'Enter valid company and team')
        
        return data