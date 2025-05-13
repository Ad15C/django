from django.urls import path
from . import views

app_name = 'mediatheque.authentification'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('connexion/', views.login_view, name='connexion'),
    path('redirect/', views.login_redirect_view, name='login-redirect'),
    path('inscription/', views.signup_view, name='inscription'),
    path('deconnexion/', views.logout_view, name='deconnexion'),
    path('modifier_profil/<int:user_id>/', views.edit_profile, name='modifier_profil'),
    path('espace_staff/', views.staff_dashboard, name='espace_staff'),
    path('espace_client/', views.client_dashboard, name='espace_client'),
]
