from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView, TemplateView, CreateView, DeleteView
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import Group
from ..companies.models import Company
from ..teams.models import Team
from ..models import Membership
from .models import User
from django.db.models import F, Count
from django.core.paginator import Paginator
from .forms import CreateUserForm, UpdateUserForm
from django.urls import reverse_lazy
from ..mixins import CheckPermissionsMixin


class LoadUsersView(LoginRequiredMixin, CheckPermissionsMixin, View):
    keyword = 'view_user'
    
    def get(self, request, *args, **kwargs):
        user = request.user
        role_name = request.GET.get('role')
        role = Group.objects.filter(name__iexact=role_name)
        email = request.GET.get('email')
        company_name = request.GET.get('company')
        company = Company.objects.filter(name__iexact=company_name)
        users = User.objects.prefetch_related('membership'
                                              ).exclude(is_superuser=True, 
                                                        role__name='system_admin'
                                                        ).annotate(
                                                            team_name=F('membership__team__name'),
                                                            team_id=F('membership__team_id'),
                                                            company_name=F('membership__company__name'),
                                                            company_id=F('membership__company_id'),
                                                            role_name=F('role__name')
                                                            ).order_by('id').values(
                                                                'id', 'email', 'first_name', 'last_name', 'last_login',
                                                                'is_active', 'role_id', 'role_name', 'company_name', 'team_id',
                                                                'company_id', 'team_name')
        teams = Team.objects.prefetch_related('company').annotate(
            members_count=Count('membership'),
            company_name=F('company__name')
        ).values('id', 'name', 'company_name', 'members_count', 'created_at')

        if not user.has_perm('users.global_view_user'):
            if user.has_perm('users.team_view_user'):
                users = users.exclude(role_name__in=['company_admin', 'team_admin']
                                      ).filter(membership__team=user.membership.team)
                teams = []
            elif user.has_perm('users.company_view_user'):
                user_company = user.membership.company
                teams = teams.filter(company=user_company)
                users = users.filter(role_name='team_admin'
                                      ).filter(membership__company=user.membership.company)
        else:
            users = users.filter(role_name='company_admin')
        
        if role:
            users = users.filter(role=role.first())

        if email:
            users = users.filter(email__contains=email)

        if company:
            users = users.filter(membership__company=company.first())

        p = Paginator(list(users), 10)
        page = p.page(request.GET.get('page', 1))
        pages = p.num_pages

        if page.number > pages or page.number < 1:
            page = p.page(1)

        return JsonResponse({'users': page.object_list,
                         'has_next': page.has_next(),
                         'has_previous': page.has_previous(),
                         'page': page.number,
                         'pages': p.num_pages,
                         'teams': list(teams),
                         'is_current_user_admin': user.role.name == 'system_admin'})


class UpdateUserView(LoginRequiredMixin, CheckPermissionsMixin, UpdateView):
    queryset = User.objects.exclude(is_superuser=True)
    form_class = UpdateUserForm
    success_url = reverse_lazy('accounts:users:all')
    password = None
    keyword = 'change_user'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['password'] = self.password
        kwargs['user'] = self.request.user
        kwargs['team'] = self.request.POST.get('team')
        kwargs['company'] = self.request.POST.get('company')
        kwargs['can_change_all_users'] = self.request.user.has_perm('users.global_change_user')

        self.can_change_all_users = kwargs['can_change_all_users']
        self.company = kwargs['company']
        self.team = kwargs['team']

        return kwargs

    def post(self, request, *args, **kwargs):
        if request.POST.get('password'):
            self.password = 'password'

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)

        permissions_roles = {
            'system_admin': 'company_admin',
            'company_admin': 'team_admin'
        }

        if not self.request.user.has_perm('users.team_change_user'):
            role = Group.objects.filter(
                name=permissions_roles[self.request.user.role.name])
            
            if role:
                user.role = role.first()

        if self.password:
            user.set_password(form.data.get('password'))

        membership = Membership.objects.get(user_id=user.id)

        if self.can_change_all_users:
            membership.company_id = self.company
        else:
            membership.company = self.request.user.membership.company
            if self.request.user.has_perm('users.company_add_user') and self.team:
                membership.team_id = self.team
                team = Team.objects.filter(id=self.team)

                if team:
                    membership.team_id = self.team  
            elif self.request.user.has_perm('users.team_add_user'):
                membership.team_id = self.request.user.membership.team_id

        membership.save()

        return super().form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        return JsonResponse(form._errors)


class AllUsersView(LoginRequiredMixin, CheckPermissionsMixin, TemplateView):
    template_name = 'accounts/users/all.html'
    keyword = 'view_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.has_perm('users.global_view_user'):
            context['roles'] = list(Group.objects.exclude(
                name='system_admin').values('id', 'name'))
            context['companies'] = list(Company.objects.values('id', 'name'))
        elif self.request.user.has_perm('users.company_view_user'):
            context['roles'] = list(Group.objects.exclude(
                name__in=['system_admin', 'company_admin']).values('id', 'name'))
        elif self.request.user.has_perm('users.team_view_user'):
            context['roles'] = list(Group.objects.exclude(
                name__in=['system_admin', 'company_admin', 'team_admin']
                ).values('id', 'name'))

        context['user_permissions'] = self.request.user.get_all_permissions()

        return context


class CreateUserView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    form_class = CreateUserForm
    template_name = 'accounts/users/create.html'
    success_url = reverse_lazy('accounts:users:all')
    keyword = 'add_user'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.data.get('password'))
        permissions_roles = {
            'system_admin': 'company_admin',
            'company_admin': 'team_admin'
        }

        if not self.request.user.has_perm('users.team_change_user'):
            role = Group.objects.filter(
                name=permissions_roles[self.request.user.role.name])
            
            if role:
                user.role = role.first()

        user.save()

        membership = Membership(user=user)

        if self.can_change_all_users:
            membership.company_id = self.company
        else:
            membership.company = self.request.user.membership.company
            if self.request.user.has_perm('users.company_add_user') and self.team:
                membership.team_id = self.team
                team = Team.objects.filter(id=self.team)

                if team:
                    membership.team_id = self.team  
            elif self.request.user.has_perm('users.team_add_user'):
                membership.team_id = self.request.user.membership.team_id
        
        membership.save()

        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['team'] = self.request.POST.get('team')
        kwargs['company'] = self.request.POST.get('company')
        kwargs['can_change_all_users'] = self.request.user.has_perm('users.global_change_user')

        self.can_change_all_users = kwargs['can_change_all_users']
        self.company = kwargs['company']
        self.team = kwargs['team']
        
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.can_change_all_users:
            context['companies'] = Company.objects.all()
            context['teams'] = Team.objects.all()
        else:
            context['teams'] = Team.objects.filter(
                    company=self.request.user.membership.company
                )

        return context