from django import forms
from .models import MediaStaff, BookStaff, DVDStaff, CDStaff, BoardGameStaff, StaffBorrowItem
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()


# Media Forms
class MediaForm(forms.ModelForm):
    class Meta:
        model = MediaStaff
        fields = ['name', 'media_type', 'is_available', 'can_borrow']


class BookForm(forms.ModelForm):
    class Meta:
        model = BookStaff
        fields = ['name', 'is_available', 'can_borrow', 'author']


class DVDForm(forms.ModelForm):
    class Meta:
        model = DVDStaff
        fields = ['name', 'is_available', 'can_borrow', 'producer']


class CDForm(forms.ModelForm):
    class Meta:
        model = CDStaff
        fields = ['name', 'is_available', 'can_borrow', 'artist']


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGameStaff
        fields = ['name', 'is_available', 'can_borrow', 'creators', 'game_type']


# Member form
class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']


# Emprunt Média
class BorrowMediaForm(forms.ModelForm):
    class Meta:
        model = apps.get_model('staff', 'StaffBorrowItem')  # Utilisation dynamique du modèle
        fields = ['media', 'due_date']
        widgets = {
            'media': forms.HiddenInput(),
            'due_date': forms.HiddenInput(),
        }

    def clean_media(self):
        # Importer le modèle MediaStaff uniquement lorsque nécessaire
        MediaStaff = apps.get_model('staff', 'MediaStaff')
        BoardGameStaff = apps.get_model('staff', 'BoardGameStaff')

        media = self.cleaned_data['media']
        if isinstance(media, BoardGameStaff):
            raise forms.ValidationError("Les jeux de société ne peuvent pas être empruntés.")
        return media
