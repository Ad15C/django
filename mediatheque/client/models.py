from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class MediaClient(models.Model):
    name = models.CharField(max_length=200)
    media_type = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    can_borrow = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    MEDIA_TYPE = None

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.media_type and self.MEDIA_TYPE:
            self.media_type = self.MEDIA_TYPE

        if not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        super().save(*args, **kwargs)

        if is_new and not self.object_id:
            self.object_id = self.id
            super().save(update_fields=['object_id'])

    def is_borrowable_by(self, user):
        return self.is_available and self.can_borrow

    @classmethod
    def get_borrowable_by(cls, user):
        return cls.objects.filter(is_available=True, can_borrow=True)

    class Meta:
        permissions = [
            ("can_view_media", "Peut voir les détails d’un média"),
        ]
        verbose_name = "Média"
        verbose_name_plural = "Médias"


# Sous-types de média (héritent de MediaClient)
class BookClient(MediaClient):
    author = models.CharField(max_length=200)
    MEDIA_TYPE = 'book'


class DVDClient(MediaClient):
    producer = models.CharField(max_length=200)
    MEDIA_TYPE = 'dvd'


class CDClient(MediaClient):
    artist = models.CharField(max_length=200)
    MEDIA_TYPE = 'cd'


class BoardGameClient(MediaClient):
    creators = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)
    game_type = models.CharField(max_length=100, blank=True, null=True)
    MEDIA_TYPE = 'board_game'

    def __str__(self):
        return self.name

    def toggle_availability(self):
        self.is_visible = not self.is_visible
        self.save(update_fields=['is_visible'])

    def is_borrowable_by(self, user):
        return False  # Non empruntable

    def save(self, *args, **kwargs):
        self.can_borrow = False
        super().save(*args, **kwargs)


# Emprunt par un client
class ClientBorrow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.ForeignKey(MediaClient, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default="user")

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
