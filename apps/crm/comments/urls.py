from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('api/get/<str:type>/<int:id>', views.GetCommentView.as_view(), name='get'),
    path('api/create/', views.CreateCommentView.as_view(), name='create')
]
