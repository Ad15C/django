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
        fields = ['name', 'is_available', 'can_borrow', 'creators', 'game_type']


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

    def clean_media(self):
        media = self.cleaned_data['media']

        # Vérifier si le média est une instance de MediaStaff
        if not isinstance(media, MediaStaff):
            raise forms.ValidationError("Le média spécifié n'est pas valide.")

        # Vérifications spécifiques selon le type de média
        if isinstance(media, BoardGameStaff):
            raise forms.ValidationError("Les jeux de société ne peuvent pas être empruntés.")

        # Validation pour les livres
        if isinstance(media, BookStaff):
            if not media.is_available:
                raise forms.ValidationError("Le livre n'est pas disponible pour emprunt.")

        # Validation pour les DVD
        if isinstance(media, DVDStaff):
            if not media.is_available:
                raise forms.ValidationError("Le DVD n'est pas disponible pour emprunt.")

        # Validation pour les CDs
        if isinstance(media, CDStaff):
            if not media.is_available:
                raise forms.ValidationError("Le CD n'est pas disponible pour emprunt.")

        # Validation générale pour tout type de MediaStaff
        if not media.is_available:
            raise forms.ValidationError(f"Le média {media.__class__.__name__} n'est pas disponible pour emprunt.")

        return media
