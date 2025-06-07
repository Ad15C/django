from django import forms
from .models import MediaStaff, BoardGameStaff, StaffBorrowItem, BookStaff, DVDStaff, CDStaff
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time
from django.utils.translation import gettext_lazy as _


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
    email = forms.EmailField(
        label="Email",
        required=True,
        error_messages={'invalid': _("Entrez une adresse email valide.")},
        widget=forms.EmailInput(attrs={'type': 'text'})
    )

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
        # Récupérer l'utilisateur passé dans les arguments
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_media(self):
        media = self.cleaned_data.get('media')

        # Débogage: Imprimer le type du média pour confirmer qu'il s'agit bien d'un jeu de société
        print(f"Type du média: {type(media)}")

        # Vérification si c'est un jeu de société
        if isinstance(media, BoardGameStaff):
            raise forms.ValidationError("Les jeux de société ne peuvent pas être empruntés.")

        # Vérification que c'est un média valide
        if not isinstance(media, MediaStaff):
            raise forms.ValidationError("Le média spécifié n\'est pas valide.")

        # Vérification de la disponibilité
        if not media.is_available:
            raise forms.ValidationError(f"Le média {media.name} n\'est pas disponible pour emprunt.")

        # Vérification si l'utilisateur peut emprunter ce média
        print(f"Validation de clean_media avec le média : {media}")

        if self.user and not media.is_borrowable_by(self.user):
            raise forms.ValidationError(f"Vous n\'êtes pas autorisé à emprunter le média {media.name}.")

        return media

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']

        today = timezone.now().date()

        # Si due_date est un datetime.date (sans heure), on convertit en datetime aware avec heure minuit
        if isinstance(due_date, datetime):
            # Si datetime naïf, rendre aware
            if timezone.is_naive(due_date):
                due_date = timezone.make_aware(due_date)
        else:
            # due_date est une date, on crée un datetime aware à minuit ce jour-là
            due_date = datetime.combine(due_date, time.min)
            due_date = timezone.make_aware(due_date)

        # Vérification des contraintes de date
        if (due_date.date() - today).days > 7:
            raise ValidationError("La date d\'échéance ne peut pas dépasser 7 jours à partir d\'aujourd\'hui.")

        if due_date.date() < today:
            raise ValidationError("La date d\'échéance ne peut pas être dans le passé.")

        return due_date
