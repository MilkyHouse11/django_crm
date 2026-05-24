from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    path('', views.AllDealsView.as_view(), name='all'),
    path('create/', views.CreateDealView.as_view(), name='create'),
    path('<int:pk>/update', views.UpdateDealView.as_view(), name='update'),
    path('api/load', views.LoadDealsView.as_view(), name='load')
]
