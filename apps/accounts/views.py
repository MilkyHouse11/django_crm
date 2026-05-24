from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from .forms import AuthenticationForm

class LoginView(DjangoLoginView):
    form_class = AuthenticationForm
    
    roles_urls = {
        'system_admin': 'accounts:companies:all',
        'company_admin': 'accounts:teams:all',
        'team_admin': 'accounts:users:all',
        'manager': 'crm:deals:all',
        'operator': 'crm:leads:all'
    }
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        self.get_redirect_url = lambda: reverse_lazy(self.roles_urls[user.role.name])
        return super().form_valid(form)