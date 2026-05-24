from django.urls import path, include


app_name = 'crm'

urlpatterns = [
    path('deals/', include('apps.crm.deals.urls')),
    path('leads/', include('apps.crm.leads.urls')),
    path('comments/', include('apps.crm.comments.urls')),
]
