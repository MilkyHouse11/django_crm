from django.urls import path, reverse_lazy, include
from django.contrib.auth.views import LogoutView
from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('users/', include('apps.accounts.users.urls')),
    path('teams/', include('apps.accounts.teams.urls')),
    path('companies/', include('apps.accounts.companies.urls'))
]