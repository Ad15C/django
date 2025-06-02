import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import Permission, ContentType
from mediatheque.staff.models import BookStaff, CDStaff, DVDStaff, BoardGameStaff
from datetime import timedelta, datetime, time
from django.test import Client

User = get_user_model()


def make_due_date(days=7):
    return timezone.make_aware(datetime.combine(timezone.now().date() + timedelta(days=days), time.min)).isoformat()


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='password123',
        role=User.STAFF,
        is_staff=True,
    )
    content_type = ContentType.objects.get(app_label='staff', model='mediastaff')
    permission = Permission.objects.get(codename='can_view_media', content_type=content_type)
    user.user_permissions.add(permission)
    user.save()
    # Recharge user pour que les permissions soient à jour (important)
    user = User.objects.get(pk=user.pk)
    return user


@pytest.mark.django_db
def test_media_list_view_with_permissions(staff_user):
    assert staff_user.has_perm('staff.can_view_media'), "L'utilisateur n'a pas la permission can_view_media"
    client = Client()
    client.force_login(staff_user)

    # Crée les médias
    BookStaff.objects.create(name="Livre Test", media_type="book", is_available=True, can_borrow=True, author="Auteur")
    CDStaff.objects.create(name="CD Test", media_type="cd", is_available=True, can_borrow=True, artist="Artiste")
    DVDStaff.objects.create(name="DVD Test", media_type="dvd", is_available=False, can_borrow=True,
                            producer="Réalisateur")
    BoardGameStaff.objects.create(name="Jeu Test", media_type="board_game", is_available=True, creators="Créateur")

    url = reverse('staff:media_liste')
    response = client.get(url)

    assert response.status_code == 200, f"Status code {response.status_code}, contenu: {response.content.decode()}"
    content = response.content.decode()
    assert "Liste des médias" in content
    assert "Livre Test" in content
    assert "CD Test" in content
    assert "DVD Test" in content
    assert "Jeu Test" in content

    # Test filtrage disponibilité
    response = client.get(url, {'available': 'true'})
    assert "DVD Test" not in response.content.decode()

    # Test filtrage type
    response = client.get(url, {'media_type': 'cd'})
    assert "CD Test" in response.content.decode()
    assert "Livre Test" not in response.content.decode()

    # Test filtrage empruntables
    response = client.get(url, {'only_borrowable': 'true'})
    content = response.content.decode()
    assert "Jeu Test" not in content  # non empruntable


@pytest.mark.django_db
def test_media_list_requires_authentication():
    client = Client()
    url = reverse('staff:media_liste')
    response = client.get(url)
    assert response.status_code == 302
    assert '/auth/connexion/' in response.url


@pytest.mark.django_db
def test_media_list_permission_denied():
    user = User.objects.create_user(
        username='no_perm',
        email='no_perm@example.com',
        password='pass',
        role=User.STAFF
    )
    client = Client()
    logged_in = client.login(username='no_perm', password='pass')
    assert logged_in, "La connexion a échoué dans le test"

    url = reverse('staff:media_liste')
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_media_list_pagination(staff_user):
    client = Client()
    client.force_login(staff_user)

    for i in range(25):
        BookStaff.objects.create(
            name=f"Livre {i}",
            media_type="book",
            is_available=True,
            can_borrow=True,
            author="Auteur"
        )

    url = reverse('staff:media_liste')

    response = client.get(url + "?page=1")
    content = response.content.decode()
    assert "Livre 0" in content
    assert "Livre 9" in content
    assert "Livre 10" not in content

    response = client.get(url + "?page=2")
    content = response.content.decode()
    assert "Livre 10" in content
    assert "Livre 19" in content
    assert "Livre 0" not in content

    response = client.get(url + "?page=3")
    content = response.content.decode()
    assert "Livre 20" in content
    assert "Livre 24" in content
