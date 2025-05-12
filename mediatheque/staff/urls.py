from django.urls import path
from authentification.views import staff_dashboard
from .views import media_views, member_views

app_name = 'staff'

urlpatterns = [
    # Dashboard
    path('espace_staff/', staff_dashboard, name='espace_staff'),

    # Médias
    path('media/liste/', media_views.media_list, name='media_liste'),
    path('media/<int:pk>/', media_views.media_detail, name='media_detail'),
    path('media/ajouter/', media_views.add_media, name='ajouter_media'),

    # Emprunts
    path('emprunter/<int:pk>/', media_views.borrow_media, name='emprunter'),
    path('emprunter/<int:pk>/detail/', media_views.borrow_detail, name='detail_emprunt'),
    path('emprunter/<int:pk>/succes/', media_views.borrow_success, name='borrow_success'),
    path('media/<int:pk>/retourner/', media_views.return_media, name='retourner_media'),

    # Membres
    path('membres/', member_views.members_list, name='liste_membres'),
    path('membres/creer/', member_views.create_member, name='creer_membre'),
    path('membres/<int:pk>/modifier/', member_views.update_member, name='modifier_membre'),
    path('membres/<int:pk>/detail/', member_views.member_detail, name='membre_detail'),
]
