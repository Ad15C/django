import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import Permission
from mediatheque.staff.models import MediaStaff, StaffBorrowItem
from django.contrib.messages import get_messages
from datetime import timedelta, datetime, time

User = get_user_model()


def make_due_date(days=7):
    return timezone.make_aware(datetime.combine(timezone.now().date() + timedelta(days=days), time.min)).isoformat()


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='password123'
    )
    user.role = User.STAFF
    user.is_staff = True

    # Ajout des permissions nécessaires
    borrow_perm = Permission.objects.get(codename='can_borrow_media')
    return_perm = Permission.objects.get(codename='can_return_media')
    user.user_permissions.add(borrow_perm, return_perm)

    user.save()
    return user



@pytest.fixture
def media(db):
    return MediaStaff.objects.create(name="Test Média", is_available=False)


@pytest.fixture
def borrow_item(db, media, staff_user):
    return StaffBorrowItem.objects.create(
        media=media,
        user=staff_user,
        is_returned=False
    )



@pytest.mark.django_db
def test_return_media_success(client, staff_user, borrow_item, media):
    client.login(username='staff', password='password123')
    url = reverse('staff:retourner_media', kwargs={'pk': borrow_item.pk})

    response = client.post(url, data={'media': media.pk})

    borrow_item.refresh_from_db()
    media.refresh_from_db()

    assert response.status_code == 302
    assert borrow_item.is_returned is True
    assert media.is_available is True


@pytest.mark.django_db
def test_return_media_wrong_media(client, staff_user, borrow_item, media):
    other_media = MediaStaff.objects.create(name="Autre Média", is_available=False)

    client.login(username='staff', password='password123')
    url = reverse('staff:retourner_media', kwargs={'pk': borrow_item.pk})
    response = client.post(url, data={'media': other_media.pk})

    borrow_item.refresh_from_db()
    assert borrow_item.is_returned is False

    messages = list(get_messages(response.wsgi_request))
    assert any("ne fait pas partie de cet emprunt" in m.message for m in messages)


@pytest.mark.django_db
def test_return_media_get_request(client, staff_user, borrow_item):
    client.login(username='staff', password='password123')
    url = reverse('staff:retourner_media', kwargs={'pk': borrow_item.pk})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('staff:detail_emprunt', kwargs={'pk': borrow_item.pk})


@pytest.mark.django_db
def test_return_media_without_permission(client, borrow_item, staff_user):
    staff_user.user_permissions.clear()
    staff_user.save()
    client.login(username='staff', password='password123')

    url = reverse('staff:retourner_media', kwargs={'pk': borrow_item.pk})
    response = client.post(url, data={'media': borrow_item.media.pk})

    assert response.status_code == 403
