from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView, View
from .models import Company
from django.core.paginator import Paginator
from ..mixins import CheckPermissionsMixin


class AllCompaniesView(LoginRequiredMixin, CheckPermissionsMixin, TemplateView):
    template_name = 'accounts/companies/all.html'
    keyword = 'view_company'


class UpdateCompanyView(LoginRequiredMixin, CheckPermissionsMixin, UpdateView):
    model = Company
    fields = ['name', 'is_active']
    success_url = reverse_lazy('accounts:companies:all')
    keyword = 'change_company'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        return JsonResponse(form._errors)
    
    def form_valid(self, form, *args, **kwargs):
        return super().form_valid(form, *args, **kwargs)


class CreateCompanyView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    model = Company
    fields = ['name']
    template_name = 'accounts/companies/create.html'
    success_url = reverse_lazy('accounts:companies:all')
    keyword = 'add_company'


class LoadCompaniesView(LoginRequiredMixin, CheckPermissionsMixin, View):
    keyword = 'view_company'

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        companies = Company.objects.values('id', 'name', 'created_at', 'is_active')

        if search:
            companies = companies.filter(name__icontains=search.strip())

        p = Paginator(list(companies), 10)
        page = p.page(request.GET.get('page', 1))

        return JsonResponse({
            'companies': page.object_list,
            'page': page.number,
            'pages': p.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous()
        })
