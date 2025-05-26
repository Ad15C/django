import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from mediatheque.staff.models import MediaStaff, StaffBorrowItem
from mediatheque.authentification.models import CustomUser


@pytest.mark.django_db
def test_confirm_borrow_view(client):
    # 1. Créer un utilisateur staff avec permission
    user = CustomUser.objects.create_user(
        username='staff_user',
        email='staff@example.com',
        password='password123',
        is_staff=True,
        role=CustomUser.STAFF
    )
    user.save()

    staff_group, _ = Group.objects.get_or_create(name='staff')
    user.groups.add(staff_group)

    permission = Permission.objects.get(codename='can_borrow_media')
    user.user_permissions.add(permission)
    user.save()

    # 2. Connexion utilisateur
    logged_in = client.login(username='staff_user', password='password123')
    assert logged_in

    # 3. Créer un média disponible
    media = MediaStaff.objects.create(name='Livre Test', is_available=True, media_type='Livre')

    # 4. Tester GET (affichage du formulaire)
    url = reverse('staff:confirmer_emprunt', args=[media.id])
    response = client.get(url)
    assert response.status_code == 200
    assert b'Confirmation de l\'emprunt' in response.content
    assert b'Livre Test' in response.content

    # 5. Tester POST (soumission du formulaire)
    due_date = (timezone.now() + timezone.timedelta(days=7)).date()
    post_data = {
        'media': media.id,
        'due_date': due_date.isoformat(),
    }
    response = client.post(url, data=post_data)

    # 6. Vérifier redirection après POST
    assert response.status_code == 302  # redirect

    # 7. Vérifier que le média est devenu indisponible
    media.refresh_from_db()
    assert media.is_available is False

    # 8. Vérifier qu’un emprunt a été créé
    borrow = StaffBorrowItem.objects.filter(media=media, user=user).first()
    assert borrow is not None
    assert borrow.due_date.date() == due_date
