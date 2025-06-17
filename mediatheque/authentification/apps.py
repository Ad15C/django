from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.apps import apps


class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mediatheque.authentification'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import CustomUser

        def create_groups_and_permissions(sender, **_):
            staff_group, _ = Group.objects.get_or_create(name='staff')
            client_group, _ = Group.objects.get_or_create(name='client')

            content_type = ContentType.objects.get_for_model(CustomUser)

            permissions_staff = [
                ('can_add_member', 'Can add members'),
                ('can_delete_member', 'Can delete member'),
                ('can_update_member', 'Can update members'),
                ('can_view_members', 'Can view members'),
                ('can_add_media', 'Can add media'),
                ('can_return_media', 'Can return media'),
                ('can_borrow_media', 'Can borrow media'),
                ('can_view_borrow', 'Can view borrow details'),
                ('can_view_media', 'Can view media'),
            ]

            permissions_client = [
                ('can_view_media', 'Can view media'),
            ]

            # Créer et assigner les permissions pour le staff
            for codename, name in permissions_staff:
                perm, _ = Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type,
                )
                staff_group.permissions.add(perm)

            # S'assurer que les permissions client existent et les assigner
            for codename, name in permissions_client:
                # On suppose ici que la permission a déjà été créée dans permissions_staff
                try:
                    perm = Permission.objects.get(
                        codename=codename,
                        content_type=content_type,
                    )
                    client_group.permissions.add(perm)
                except Permission.DoesNotExist:
                    pass  # ou logguer une erreur si besoin

        post_migrate.connect(create_groups_and_permissions, sender=apps.get_app_config('authentification'))
