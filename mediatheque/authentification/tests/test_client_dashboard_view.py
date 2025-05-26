import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from mediatheque.staff.models import StaffBorrowItem, MediaStaff

User = get_user_model()


@pytest.fixture
def client_user(db):
    user = User.objects.create_user(
        username='client1',
        email='client1@example.com',
        password='testpass123',
        role=User.CLIENT,
        first_name='Jean',
        last_name='Dupont'
    )
    return user


@pytest.fixture
def other_user(db):
    user = User.objects.create_user(
        username='staff1',
        email='staff1@example.com',
        password='testpass123',
        role='STAFF'
    )
    return user


@pytest.fixture
def media_items(db):
    media1 = MediaStaff.objects.create(name='Media 1', is_available=True, can_borrow=True)
    media2 = MediaStaff.objects.create(name='Media 2', is_available=True, can_borrow=True)
    return [media1, media2]


@pytest.fixture
def borrow_item(db, client_user, media_items):
    return StaffBorrowItem.objects.create(user=client_user, media=media_items[0], is_returned=False)


@pytest.mark.django_db
def test_client_dashboard_access_authorized(client_user):
    c = Client()
    c.login(username='client1', password='testpass123')
    url = reverse('authentification:espace_client')
    response = c.get(url)
    assert response.status_code == 200
    assert b'Bienvenue, client1' in response.content


@pytest.mark.django_db
def test_client_dashboard_access_forbidden(client, django_user_model):
    staff_user = django_user_model.objects.create_user(
        username='staffuser',
        email='staffuser@example.com',
        password='testpass123',
        role=User.STAFF
    )
    client.login(username='staffuser', password='testpass123')
    response = client.get(reverse('authentification:espace_client'))
    assert response.status_code == 403  # Forbidden


@pytest.mark.django_db
def test_client_dashboard_shows_borrows_and_media(client_user, borrow_item, media_items):
    c = Client()
    c.login(username='client1', password='testpass123')
    url = reverse('authentification:espace_client')
    response = c.get(url)
    assert b'Media 1' in response.content  # L’emprunt en cours
    assert b'Media 1' in response.content
    assert b'Media 2' in response.content


@pytest.mark.django_db
def test_client_dashboard_no_borrows_message(client_user, media_items):
    c = Client()
    c.login(username='client1', password='testpass123')
    url = reverse('authentification:espace_client')
    response = c.get(url)

    # Compare the decoded content with the string
    assert 'Aucune réservation en cours' in response.content.decode('utf-8')
