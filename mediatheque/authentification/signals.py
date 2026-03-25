from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def sync_user_role_groups(sender, instance, **kwargs):
    staff_group, _ = Group.objects.get_or_create(name='staff')
    client_group, _ = Group.objects.get_or_create(name='client')

    if instance.role == CustomUser.STAFF:
        if not instance.is_staff:
            CustomUser.objects.filter(pk=instance.pk).update(is_staff=True)

        instance.groups.add(staff_group)
        instance.groups.remove(client_group)

    elif instance.role == CustomUser.CLIENT:
        if instance.is_staff:
            CustomUser.objects.filter(pk=instance.pk).update(is_staff=False)

        instance.groups.add(client_group)
        instance.groups.remove(staff_group)

    else:
        # cas de rôle inconnu / intrus / autre
        if instance.is_staff:
            CustomUser.objects.filter(pk=instance.pk).update(is_staff=False)

        instance.groups.remove(staff_group, client_group)