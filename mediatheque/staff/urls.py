from django.urls import path
from .views import media_views

app_name = 'staff'

urlpatterns = [
    path('emprunter/<int:media_id>/', media_views.borrow_media, name='emprunter'),
]
