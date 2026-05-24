from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.AllLeadsView.as_view(), name='all'),
    path('create/', views.CreateLeadView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateLeadView.as_view(), name='update'),
    path('api/load/', views.LoadLeadsView.as_view(), name='load')
]
