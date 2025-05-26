import pytest
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Permission
from mediatheque.authentification.models import CustomUser
from mediatheque.staff.models import StaffBorrowItem, MediaStaff

def make_due_date(days=7):
    return timezone.make_aware(datetime.combine(timezone.now().date() + timedelta(days=days), time.min)).isoformat()



# Utilisateur STAFF avec permission
@pytest.fixture
def staff_user_with_permission(db):
    user = CustomUser.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='pass1234',
        role=CustomUser.STAFF
    )
    permission = Permission.objects.get(codename='can_borrow_media')
    user.user_permissions.add(permission)
    user.save()
    return user


# Utilisateur CLIENT
@pytest.fixture
def client_user(db):
    return CustomUser.objects.create_user(
        username='clientuser',
        email='client@example.com',
        password='pass1234',
        role=CustomUser.CLIENT
    )


# Média test
@pytest.fixture
def media(db):
    return MediaStaff.objects.create(name="Test Media", media_type="Livre")


# Emprunt par un STAFF
@pytest.fixture
def borrow_item(db, media, staff_user_with_permission):
    return StaffBorrowItem.objects.create(
        media=media,
        borrow_date=timezone.make_aware(datetime(2025, 5, 1)),
        due_date=timezone.make_aware(datetime(2025, 5, 15)),
        user=staff_user_with_permission
    )


# Emprunt par un CLIENT
@pytest.fixture
def borrow_item_for_client(db, media, client_user):
    return StaffBorrowItem.objects.create(
        media=media,
        borrow_date=timezone.make_aware(datetime(2025, 5, 1)),
        due_date=timezone.make_aware(datetime(2025, 5, 15)),
        user=client_user
    )


@pytest.mark.django_db
def test_borrow_success_view(client, staff_user_with_permission, borrow_item, media):
    client.login(username='staffuser', password='pass1234')

    url = reverse('staff:succes_emprunt', kwargs={'pk': borrow_item.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'staff/media/borrow_success.html' in [t.name for t in response.templates]
    assert response.context['borrow_item'] == borrow_item
    assert response.context['media'] == media


@pytest.mark.django_db
def test_borrow_success_view_permission_denied(client, borrow_item):
    url = reverse('staff:succes_emprunt', kwargs={'pk': borrow_item.pk})
    response = client.get(url)

    assert response.status_code == 302
    login_url = reverse('authentification:connexion')
    assert login_url in response.url


@pytest.mark.django_db
def test_borrow_success_view_forbidden_for_wrong_role(client, client_user, borrow_item_for_client):
    client.login(username='clientuser', password='pass1234')

    url = reverse('staff:succes_emprunt', kwargs={'pk': borrow_item_for_client.pk})
    response = client.get(url)

    assert response.status_code == 403
