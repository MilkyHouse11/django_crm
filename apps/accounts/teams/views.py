from .models import Team
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, CreateView, View, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count, F
from django.core.paginator import Paginator
from ..mixins import CheckPermissionsMixin
from ..companies.models import Company
from django import forms

User = get_user_model()


class UpdateTeamView(LoginRequiredMixin, CheckPermissionsMixin, UpdateView):
    model = Team
    model = Team
    fields = ['name', 'is_active']
    success_url = reverse_lazy('accounts:teams:all')
    keyword = 'change_team'

    def form_invalid(self, form, *args, **kwargs):
        return JsonResponse(form._errors)


class CreateTeamView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    model = Team
    fields = ['name', 'company']
    template_name = 'accounts/teams/create.html'
    success_url = reverse_lazy('accounts:teams:all')
    keyword = 'add_team'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['company'] = forms.ModelChoiceField(
            queryset=Company.objects.filter(id=self.request.user.membership.company.id),
            initial=self.request.user.membership.company,
            widget=forms.HiddenInput()
        )
        return form

    
    # def form_valid(self, form):
    #     team = form.save(commit=False)
    #     team.company = self.request.user.membership.company

    #     return super().form_valid(form)


class LoadTeamsView(LoginRequiredMixin, CheckPermissionsMixin, View):
    keyword = 'view_team'

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')

        teams = Team.objects.prefetch_related('company').prefetch_related('membership').annotate(
            members_count=Count('membership'),
            company_name=F('company__name')
        ).values('id', 'name', 'company_name', 'company_id', 'members_count', 'created_at', 'is_active')

        if not request.user.has_perm('accounts.view_team'):
            user_company = request.user.membership.company
            teams = teams.filter(company=user_company)
        else:
            company = request.GET.get('company')

            if company and company != 'all':
                teams = teams.filter(company__name=company)

        if search:
            teams = teams.filter(name__icontains=search.strip())

        p = Paginator(list(teams), 10)
        page = p.page(request.GET.get('page', 1))

        return JsonResponse({
            'teams': page.object_list,
            'page': page.number,
            'pages': p.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
            'is_current_user_admin': request.user.has_perm('accounts.view_team')
        })


class AllTeamsView(LoginRequiredMixin, CheckPermissionsMixin, TemplateView):
    template_name = 'accounts/teams/all.html'
    keyword = 'view_team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context