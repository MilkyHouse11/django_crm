from django.views.generic import CreateView, TemplateView, View
from django.views.generic.edit import DeleteView, UpdateView
from .models import Lead
from django.contrib.auth import get_user_model
from .enums import LeadStatus, LeadSource
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import CharField
from django.db.models.functions import Cast
from .forms import CreateLeadForm, UpdateLeadForm
from ..mixins import CheckPermissionsMixin

User = get_user_model()


class LoadLeadsView(LoginRequiredMixin, CheckPermissionsMixin, View):
    keyword = 'view_lead'

    def get(self, request, *args, **kwargs):
        source = request.GET.get('source')
        status = request.GET.get('status')
        search = request.GET.get('search')

        leads = Lead.objects.order_by(
            'id'
            ).annotate(phone_number=Cast('phone', CharField())
                       ).prefetch_related('assigned_to'
                                          ).values('id', 'full_name', 'email',
                                                   'phone_number', 'source', 'status',
                                                   'assigned_to__email', 'created_at',
                                                   'is_active'
                                                   )

        if request.user.has_perm('leads.team_view_lead'):
            if request.user.role.name == 'operator':
                leads = leads.filter(created_by=request.user, status=LeadStatus.NEW)
            else:
                leads = leads.filter(team=request.user.membership.team, assigned_to=None)
        elif request.user.has_perm('leads.local_view_lead'):
            leads = leads.filter(assigned_to=request.user)

        if source in LeadSource.values:
            leads = leads.filter(source=source)

        if status in LeadStatus.values:
            leads = leads.filter(status=status)

        if search:
            leads = leads.filter(full_name__icontains=search)

        p = Paginator(list(leads), 10)
        page = p.page(request.GET.get('page', 1))

        return JsonResponse({
            'leads': page.object_list,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
            'page': page.number,
            'pages': p.num_pages,
            'is_current_user_manager': request.user.role.name == 'manager'
        })


class UpdateLeadView(LoginRequiredMixin, CheckPermissionsMixin, UpdateView):
    form_class = UpdateLeadForm
    queryset = Lead.objects.all()
    success_url = reverse_lazy('crm:leads:all')
    keyword = 'change_lead'

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_perm('leads.team_view_lead'):
            if request.user.role.name == 'operator':
                self.queryset = Lead.objects.filter(
                    created_by=request.user, status=LeadStatus.NEW
                )
            else:
                self.queryset = Lead.objects.filter(
                    team=request.user.membership.team, assigned_to=None
                )
        elif request.user.has_perm('leads.local_view_lead'):
            self.queryset = Lead.objects.filter(assigned_to=request.user)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_invalid(self, form, *args, **kwargs):
        return JsonResponse(form._errors)


class AllLeadsView(LoginRequiredMixin, CheckPermissionsMixin, TemplateView):
    template_name = 'crm/leads/all.html'
    keyword = 'view_lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['statuses'] = LeadStatus.values
        context['sources'] = LeadSource.values
        context['managers'] = list(
            User.objects.prefetch_related(
                'role'
                ).filter(role__name='manager').values('id', 'email'))

        if self.request.user.has_perm('leads.team_view_lead'):
            context['managers'] = list(
                User.objects.prefetch_related(
                                    'role', 
                                    'membership'
                                    ).filter(
                                        role__name='manager',
                                        membership__team=self.request.user.membership.team
                                        ).values('id', 'email'))
        elif self.request.user.has_perm('leads.local_view_lead'):
            context['managers'] = None

        context['current_user_role'] = self.request.user.role.name
        context['update_url'] = reverse_lazy('crm:leads:update', args=[1])

        return context


class CreateLeadView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    form_class = CreateLeadForm
    template_name = 'crm/leads/create.html'
    success_url = reverse_lazy('crm:leads:all')
    keyword = 'add_lead'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.created_by = self.request.user
        lead.status = LeadStatus.NEW
        lead.company = self.request.user.membership.company
        lead.team = self.request.user.membership.team

        if not self.request.user.has_perm('team_add_lead'):
            lead.assigned_to = self.request.user

        return super().form_valid(form)