from django.urls import path
from . import views


app_name = 'client'

urlpatterns = [
    path('espace_client/', views.client_dashboard, name='espace_client'),
]
