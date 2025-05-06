from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

# Obtenez l'utilisateur personnalisé
User = get_user_model()

MAX_BORROW_DURATION_DAYS = 7


# Modèle de base pour les emprunts
class StaffBorrowItem(models.Model):
    user = models.ForeignKey(
        'authentification.CustomUser',
        on_delete=models.CASCADE,
        related_name='staff_borrow_items'
    )
    media = models.ForeignKey(
        'MediaStaff',
        on_delete=models.CASCADE,
        related_name='staff_borrows_media'
    )
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.due_date = timezone.now() + timezone.timedelta(days=MAX_BORROW_DURATION_DAYS)
        if self.is_returned and not self.return_date:
            self.return_date = timezone.now()
        super().save(*args, **kwargs)

    @staticmethod
    def can_borrow(user):
        # Vérifier s'il y a déjà 3 emprunts actifs
        active_borrows = StaffBorrowItem.objects.filter(user=user, is_returned=False)
        if active_borrows.count() >= 3:
            return False

        # Vérifier si un emprunt est en retard
        overdue_borrows = StaffBorrowItem.objects.filter(
            user=user,
            is_returned=False,
            due_date__lt=timezone.now()
        )

        # L'utilisateur peut emprunter si aucun emprunt n'est en retard
        return not overdue_borrows.exists()


# Modèle de base pour Media
class MediaStaff(models.Model):
    name = models.CharField(max_length=200)
    media_type = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)  # Use is_available in MediaStaff base model
    can_borrow = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_borrowable_by(self, user):
        if not self.is_available or not self.can_borrow:
            return False

        # Vérifie si un emprunt est déjà en cours
        current_borrow = StaffBorrowItem.objects.filter(media=self, is_returned=False).first()
        if current_borrow:
            return False  # Le média est déjà emprunté

        # Si l'utilisateur a un rôle autorisé, il peut emprunter
        if user.role not in [User.CLIENT, User.STAFF]:
            return False  # L'utilisateur n'a pas les droits nécessaires

        return True

    @classmethod
    def get_borrowable_by(cls, user):
        return [media for media in cls.objects.all() if media.is_borrowable_by(user)]


# Modèles spécifiques : Livre, DVD, CD, Jeu de Plateau
class BookStaff(MediaStaff):
    author = models.CharField(max_length=200)
    available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'book'
        self.content_type = ContentType.objects.get_for_model(BookStaff)
        super().save(*args, **kwargs)


class DVDStaff(MediaStaff):
    producer = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'dvd'
        self.content_type = ContentType.objects.get_for_model(DVDStaff)
        super().save(*args, **kwargs)


class CDStaff(MediaStaff):
    artist = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'cd'
        self.content_type = ContentType.objects.get_for_model(CDStaff)
        super().save(*args, **kwargs)


class BoardGameStaff(MediaStaff):  # Inherits is_available from MediaStaff
    creators = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)
    game_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def toggle_availability(self):
        if not StaffBorrowItem.objects.filter(media=self, is_returned=False).exists():
            self.is_available = not self.is_available
            self.save(update_fields=['is_available'])

    def can_borrow(self):
        return False  # Les jeux de plateau ne peuvent pas être empruntés

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'board_game'
        self.can_borrow = False  # Ne permet pas l'emprunt des jeux de plateau
        super().save(*args, **kwargs)
