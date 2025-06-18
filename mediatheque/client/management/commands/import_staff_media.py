from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from mediatheque.staff.models import BookStaff, CDStaff, DVDStaff, BoardGameStaff
from mediatheque.client.models import MediaClient, BookClient, CDClient, DVDClient, BoardGameClient


class Command(BaseCommand):
    help = "Importer les médias de l'app staff vers l'app client avec content_type et object_id"

    def handle(self, *args, **options):
        self.import_books()
        self.import_cds()
        self.import_dvds()
        self.import_boardgames()
        self.stdout.write(self.style.SUCCESS("Import terminé avec succès."))

    def _create_or_update_media(self, staff_obj, client_model):
        content_type = ContentType.objects.get_for_model(staff_obj)
        # Vérifier si MediaClient existe déjà pour ce staff_obj
        media_client = MediaClient.objects.filter(content_type=content_type, object_id=staff_obj.id).first()

        defaults = {
            "name": staff_obj.name,
            "media_type": client_model.MEDIA_TYPE,
            "is_available": getattr(staff_obj, "is_available", True),
            "can_borrow": getattr(staff_obj, "can_borrow", True),
            "description": getattr(staff_obj, "description", ""),
            "content_type": content_type,
            "object_id": staff_obj.id,
        }

        if media_client:
            # Mise à jour
            for key, value in defaults.items():
                setattr(media_client, key, value)
            media_client.save()
            created = False
        else:
            # Création
            media_client = MediaClient.objects.create(**defaults)
            created = True

        # Maintenant on synchronise le sous-type client, lié à MediaClient
        client_obj = client_model.objects.filter(id=media_client.id).first()
        if not client_obj:
            # Crée une entrée dans la table spécifique client avec le même id
            client_obj = client_model(id=media_client.id)

        # Compléter champs spécifiques
        if client_model == BookClient:
            client_obj.author = getattr(staff_obj, "author", "")
        elif client_model == CDClient:
            client_obj.artist = getattr(staff_obj, "artist", "")
        elif client_model == DVDClient:
            client_obj.producer = getattr(staff_obj, "producer", "")
        elif client_model == BoardGameClient:
            client_obj.creators = getattr(staff_obj, "creators", "")
            client_obj.is_visible = getattr(staff_obj, "is_visible", True)
            client_obj.game_type = getattr(staff_obj, "game_type", None)
            client_obj.can_borrow = False  # Comme dans ton modèle

        client_obj.save()

        action = "Créé" if created else "Mis à jour"
        self.stdout.write(f"{action} média: {media_client.name} ({client_model.__name__})")

    def import_books(self):
        for book in BookStaff.objects.all():
            self._create_or_update_media(book, BookClient)

    def import_cds(self):
        for cd in CDStaff.objects.all():
            self._create_or_update_media(cd, CDClient)

    def import_dvds(self):
        for dvd in DVDStaff.objects.all():
            self._create_or_update_media(dvd, DVDClient)

    def import_boardgames(self):
        for game in BoardGameStaff.objects.all():
            self._create_or_update_media(game, BoardGameClient)
