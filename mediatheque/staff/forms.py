from django import forms
from staff.models import MediaStaff, BookStaff, DVDStaff, CDStaff, BoardGameStaff
from django.contrib.auth import get_user_model

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
