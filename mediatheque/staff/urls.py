from django.urls import path
from .views import media_views

app_name = 'staff'

urlpatterns = [
    # Médias
    path('media/liste/', media_views.media_list, name='media_liste'),
    path('media/<int:pk>/', media_views.media_detail, name='media_detail'),
    path('media/ajouter/', media_views.add_media, name='ajouter_media'),
    path('emprunter/<int:pk>/', media_views.borrow_media, name='emprunter'),
    path('emprunter/<int:pk>/detail/', media_views.borrow_detail, name='detail_emprunt'),
    path('media/<int:pk>/retourner/', media_views.return_media, name='retourner_media'),
]
