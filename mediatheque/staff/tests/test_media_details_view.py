import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from mediatheque.staff.models import BoardGameStaff, CDStaff, DVDStaff, BookStaff, MediaStaff
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


@pytest.fixture
def staff_user_with_permission(db):
    user = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="password123",
        role=User.STAFF,
        is_staff=True
    )
    content_type = ContentType.objects.get_for_model(MediaStaff)
    perm = Permission.objects.get(codename='can_view_media', content_type=content_type)
    user.user_permissions.add(perm)
    user.save()
    return user


@pytest.fixture
def book(db):
    return BookStaff.objects.create(
        name="Livre Test",
        author="Auteur Exemple",
        description="Description livre test",
        is_available=True,
        can_borrow=True,
    )


@pytest.fixture
def dvd(db):
    return DVDStaff.objects.create(
        name="DVD Test",
        producer="Producteur Exemple",
        description="Description DVD test",
        is_available=True,
        can_borrow=True,
    )


@pytest.fixture
def cd(db):
    return CDStaff.objects.create(
        name="CD Test",
        artist="Artiste Exemple",
        description="Description CD test",
        is_available=True,
        can_borrow=True,
    )


@pytest.fixture
def boardgame(db):
    return BoardGameStaff.objects.create(
        name="Jeu de Société Test",
        creators="Créateurs Exemple",
        description="Description jeu de société",
        is_visible=True,
        is_available=True,
        can_borrow=False,
    )


@pytest.fixture
def media_with_description(db):
    # Exemple avec un livre
    return BookStaff.objects.create(
        name="Livre avec description",
        author="Auteur Test",
        description="Ceci est une description de test.",
        is_available=True,
        can_borrow=True,
    )


@pytest.mark.django_db
@pytest.mark.parametrize("media_fixture", ["book", "dvd", "cd", "boardgame"])
def test_media_detail_for_each_type(client, staff_user_with_permission, request, media_fixture):
    media = request.getfixturevalue(media_fixture)
    client.login(username='staff', password='password123')
    url = reverse('staff:media_detail', kwargs={'pk': media.pk})
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert media.name in content
    assert media.description in content


@pytest.mark.django_db
def test_media_detail_view_success(client, staff_user_with_permission, book):
    assert client.login(username='staff', password='password123')
    url = reverse('staff:media_detail', kwargs={'pk': book.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert "Détails du média" in response.content.decode()
    assert book.name in response.content.decode()



@pytest.mark.django_db
def test_media_detail_no_permission(client, media_with_description):
    # Utilisateur sans permission
    user = User.objects.create_user(
        username="staff2",
        email="staff2@example.com",
        password="password123",
        role=User.STAFF,
        is_staff=True
    )

    client.login(username='staff2', password='password123')

    url = reverse('staff:media_detail', kwargs={'pk': media_with_description.pk})
    response = client.get(url)

    assert response.status_code == 403
