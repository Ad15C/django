from django.db import models
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
        'Media',
        on_delete=models.CASCADE,
        related_name='staff_borrows_media'
    )
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timezone.timedelta(days=MAX_BORROW_DURATION_DAYS)
        if self.is_returned and not self.return_date:
            self.return_date = timezone.now()
        super().save(*args, **kwargs)

    def is_overdue(self):
        return not self.is_returned and self.due_date < timezone.now()

    @staticmethod
    def can_borrow(user):
        active_borrows = StaffBorrowItem.objects.filter(user=user, is_returned=False)
        if active_borrows.count() >= 3:
            return False
        overdue_borrows = active_borrows.filter(due_date__lt=timezone.now())
        return not overdue_borrows.exists()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_returned']),
        ]


# Modèle de base pour Media
class MediaStaff(models.Model):
    name = models.CharField(max_length=200)
    media_type = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    can_borrow = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_borrowable_by(self, user):
        if not self.is_available or not self.can_borrow:
            return False
        current_borrow = StaffBorrowItem.objects.filter(media=self, is_returned=False).first()
        if current_borrow:
            return False
        if user.role not in [User.CLIENT, User.STAFF]:
            return False
        return True

    @classmethod
    def get_borrowable_by(cls, user):
        return cls.objects.filter(is_available=True, can_borrow=True).exclude(
            staff_borrows_media__is_returned=False
        )

    class Meta:
        pass


class Media(MediaStaff):
    pass


# Modèles spécifiques : Livre, DVD, CD, Jeu de Plateau
class BookStaff(MediaStaff):
    author = models.CharField(max_length=200)
    available = models.BooleanField(default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'book'

        self.content_type = ContentType.objects.get_for_model(BookStaff)

        self.object_id = self.id
        super().save(*args, **kwargs)


class DVDStaff(MediaStaff):
    producer = models.CharField(max_length=200)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'dvd'
        self.content_type = ContentType.objects.get_for_model(DVDStaff)
        self.object_id = self.id
        super().save(*args, **kwargs)


class CDStaff(MediaStaff):
    artist = models.CharField(max_length=200)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'cd'
        self.content_type = ContentType.objects.get_for_model(CDStaff)
        self.object_id = self.id  # Assurez-vous de définir object_id correctement
        super().save(*args, **kwargs)


class BoardGameStaff(MediaStaff):
    creators = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)
    game_type = models.CharField(max_length=100, blank=True, null=True)

    # Champs nécessaires pour le GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name

    def toggle_availability(self):
        if not StaffBorrowItem.objects.filter(media=self, is_returned=False).exists():
            self.is_available = not self.is_available
            self.save(update_fields=['is_available'])

    def is_borrowable_by(self, user):
        return False

    def save(self, *args, **kwargs):
        if not self.media_type:
            self.media_type = 'board_game'
        self.can_borrow = False  # Ne permet pas l'emprunt des jeux de plateau
        self.content_type = ContentType.objects.get_for_model(BoardGameStaff)
        self.object_id = self.id
        super().save(*args, **kwargs)
