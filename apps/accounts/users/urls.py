from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('', views.AllUsersView.as_view(), name='all'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateUserView.as_view(), name='update'),
    path('api/load', views.LoadUsersView.as_view(), name='load')
]
