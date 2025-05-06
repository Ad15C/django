from django.urls import path, include
from authentification.views import client_dashboard
from . import views

app_name = 'client'

urlpatterns = [
    path('espace_client', views.client_dashboard, name='espace_client'),
]
