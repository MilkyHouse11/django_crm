from django.urls import path
from . import views


app_name = 'companies'

urlpatterns = [
    path('', views.AllCompaniesView.as_view(), name='all'),
    path('create/', views.CreateCompanyView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateCompanyView.as_view(), name='update'),
    path('api/load', views.LoadCompaniesView.as_view(), name='load')
]
