from django import forms
from .models import MediaStaff, BoardGameStaff, StaffBorrowItem, BookStaff, DVDStaff, CDStaff
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
        fields = ['name', 'is_available', 'creators', 'game_type']


# Member form
class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']


# Emprunt Média
class BorrowMediaForm(forms.ModelForm):
    class Meta:
        model = StaffBorrowItem
        fields = ['media', 'due_date']
        widgets = {
            'media': forms.HiddenInput(),
            'due_date': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_media(self):
        media = self.cleaned_data['media']

        if not isinstance(media, MediaStaff):
            raise forms.ValidationError("Le média spécifié n'est pas valide.")

        if isinstance(media, BoardGameStaff):
            raise forms.ValidationError("Les jeux de société ne peuvent pas être empruntés.")

        if not media.is_available:
            raise forms.ValidationError(f"Le média {media.name} n'est pas disponible pour emprunt.")

        if self.user and not media.is_borrowable_by(self.user):
            raise forms.ValidationError(f"Vous n'êtes pas autorisé à emprunter le média {media.name}.")

        return media
