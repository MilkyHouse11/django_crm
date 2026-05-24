from django.urls import path
from . import views


app_name = 'teams'

urlpatterns = [
    path('', views.AllTeamsView.as_view(), name='all'),
    path('create/', views.CreateTeamView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateTeamView.as_view(), name='update'),
    path('api/load', views.LoadTeamsView.as_view(), name='load')
]
