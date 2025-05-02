from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone

# Obtenez l'utilisateur personnalisé
User = get_user_model()

MAX_BORROW_DURATION_DAYS = 7


# Modèle de base pour les emprunts
class StaffBorrowItem(models.Model):
    user = models.ForeignKey(
        'authentification.CustomUser',
        on_delete=models.CASCADE,
        related_name='staff_borrow_items'  # This remains unchanged
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
        active_borrows = StaffBorrowItem.objects.filter(user=user, is_returned=False)
        if active_borrows.count() >= 3:
            return False

        overdue_borrows = active_borrows.filter(due_date__lt=timezone.now())
        if overdue_borrows.exists():
            return False

        return True

    def __str__(self):
        return f"{self.user.username} a emprunté {self.media.name}"


# Modèle de base pour Media
class MediaStaff(models.Model):
    name = models.CharField(max_length=200)
    media_type = models.CharField(max_length=50)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Modèles spécifiques : Livre, DVD, CD, Jeu de Plateau
class BookStaff(MediaStaff):
    author = models.CharField(max_length=200)

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


class BoardGameStaff(MediaStaff):
    creators = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    game_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def toggle_availability(self):
        with transaction.atomic():
            if not StaffBorrowItem.objects.filter(media=self, is_returned=False).exists():
                self.is_available = not self.is_available
                self.save(update_fields=['is_available'])

    def can_borrow(self):
        return False  # Les jeux de plateau ne peuvent pas être empruntés

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'board_game'
        self.content_type = ContentType.objects.get_for_model(BoardGameStaff)
        super().save(*args, **kwargs)
