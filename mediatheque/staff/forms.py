from django import forms
from staff.models import MediaStaff, BookStaff, DVDStaff, CDStaff, BoardGameStaff


# staff/forms.py
from django import forms
from staff.models import MediaStaff, BookStaff, DVDStaff, CDStaff, BoardGameStaff


class MediaForm(forms.ModelForm):
    class Meta:
        model = MediaStaff
        fields = ['name', 'media_type', 'is_available', 'can_borrow']

    author = forms.CharField(max_length=200, required=False)
    producer = forms.CharField(max_length=200, required=False)
    artist = forms.CharField(max_length=200, required=False)
    creators = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ajouter 'author' uniquement pour les livres
        if isinstance(self.instance, BookStaff):
            self.fields['author'].required = True
        else:
            self.fields.pop('author', None)

        # Ajouter 'producer' uniquement pour les DVDs
        if isinstance(self.instance, DVDStaff):
            self.fields['producer'].required = True
        else:
            self.fields.pop('producer', None)

        # Ajouter 'artist' uniquement pour les CDs
        if isinstance(self.instance, CDStaff):
            self.fields['artist'].required = True
        else:
            self.fields.pop('artist', None)

        # Ajouter 'creators' uniquement pour les jeux de plateau
        if isinstance(self.instance, BoardGameStaff):
            self.fields['creators'].required = True
        else:
            self.fields.pop('creators', None)


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGameStaff
        fields = ['creators', 'is_visible', 'game_type']
