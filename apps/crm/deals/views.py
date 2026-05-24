from django.views.generic import CreateView, TemplateView, View
from django.views.generic.edit import DeleteView, UpdateView
from .models import Deal
from ..leads.models import Lead
from ..leads.enums import LeadStatus
from .enums import DealStage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from .forms import CreateDealForm, UpdateDealForm
from django.core.paginator import Paginator
from django.db.models import F
from datetime import datetime
from ..mixins import CheckPermissionsMixin


class LoadDealsView(LoginRequiredMixin, CheckPermissionsMixin, View):
    login_url = reverse_lazy('accounts:login')
    keyword = 'view_deal'

    def get(self, request, *args, **kwargs):
        stages = DealStage.values
        stage = request.GET.get('stage')
        title = request.GET.get('search')
        datel = request.GET.get('datel')
        dateg = request.GET.get('dateg')

        deals = Deal.objects.filter(
            lead__assigned_to=request.user
            ).order_by('id').prefetch_related('lead'
                                              ).annotate(lead_name=F('lead__full_name')
                                                         ).values('id', 'lead_name', 'lead_id',
                                                                  'title', 'expected_amount',
                                                                  'actual_amount', 'stage', 'probability',
                                                                  'expected_close_date', 'closed_at')

        if stage in stages:
            deals = deals.filter(stage=stage)

        if title:
            deals = deals.filter(title__contains=title)

        if datel or dateg:
            format_str = "%Y-%m-%d"

            if datel:
                deals = deals.filter(
                    expected_close_date__lte=datetime.strptime(datel, format_str))
            if dateg:
                deals = deals.filter(
                    expected_close_date__gte=datetime.strptime(dateg, format_str))

        p = Paginator(list(deals), 10)
        page = p.page(request.GET.get('page', 1))

        return JsonResponse({'deals': page.object_list,
                             'has_next': page.has_next(),
                             'has_previous': page.has_previous(),
                             'page': page.number,
                             'pages': p.num_pages,
                             'stages': stages})


class UpdateDealView(LoginRequiredMixin, CheckPermissionsMixin, UpdateView):
    login_url = reverse_lazy('accounts:login')
    model = Deal
    success_url = reverse_lazy('crm:deals:all')
    form_class = UpdateDealForm
    keyword = 'change_deal'

    def form_invalid(self, form, *args, **kwargs):
        return JsonResponse(form._errors)


class CreateDealView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    login_url = reverse_lazy('accounts:login')
    template_name = 'crm/deals/create.html'
    success_url = reverse_lazy('crm:deals:all')
    form_class = CreateDealForm
    keyword = 'add_deal'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        deal = form.save(commit=False)
        deal.team = self.request.user.membership.team
        deal.company = self.request.user.membership.company

        return super().form_valid(form)    


class AllDealsView(LoginRequiredMixin, CheckPermissionsMixin, TemplateView):
    login_url = reverse_lazy('accounts:login')
    template_name = 'crm/deals/all.html'
    keyword = 'view_deal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = DealStage.values
        context['can_create_deal'] = [
            p for p in self.request.user.get_all_permissions() if 'add_deal' in p
        ]
        context['update_url'] = reverse_lazy('crm:deals:update', args=[1])

        return context
