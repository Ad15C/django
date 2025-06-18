import pytest
from django.urls import reverse
from mediatheque.client.models import MediaClient, ClientBorrow, BookClient, DVDClient, CDClient, BoardGameClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


@pytest.fixture
def client_user(db):
    user, created = User.objects.get_or_create(username="client", defaults={"email": "client@example.com"})
    if created:
        user.set_password("test1234")
        user.role = "client"  # Important
        user.save()
    return user


@pytest.mark.django_db
def test_reverse_client_espace_client():
    url = reverse("client:espace_client")
    assert url == "/client/espace_client/"


@pytest.mark.django_db
def test_client_dashboard_view(client, client_user):
    media1 = MediaClient.objects.create(name="Media A", is_available=True, can_borrow=True)
    media2 = MediaClient.objects.create(name="Media B", is_available=False, can_borrow=True)

    assert client.login(username="client", password="test1234")

    url = reverse("client:espace_client")
    response = client.get(url)

    assert response.status_code == 200
    assert "Media A" in response.content.decode()
    assert "Media B" not in response.content.decode()


@pytest.mark.django_db
def test_client_dashboard_with_borrows(client, client_user):
    media = MediaClient.objects.create(name="Media C", is_available=True, can_borrow=True)
    ClientBorrow.objects.create(user=client_user, media=media)

    assert client.login(username="client", password="test1234")

    url = reverse("client:espace_client")
    response = client.get(url)

    assert "Media C" in response.content.decode()
    assert "Vous n'avez aucun emprunt en cours" not in response.content.decode()


@pytest.mark.django_db
def test_dashboard_forbidden_for_non_clients(client):
    user = User.objects.create_user(username="intrus", email="intrus@example.com", password="test1234")
    user.role = "intrus"
    user.save()

    assert client.login(username="intrus", password="test1234")

    response = client.get(reverse("client:espace_client"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_bookclient_creation_and_display(client, client_user):
    book = BookClient.objects.create(name="Livre Test", author="Auteur Test", is_available=True, can_borrow=True)
    assert client.login(username="client", password="test1234")

    response = client.get(reverse("client:espace_client"))
    assert "Livre Test" in response.content.decode()
    assert book.media_type == "book"


@pytest.mark.django_db
def test_dvdclient_creation_and_display(client, client_user):
    dvd = DVDClient.objects.create(name="DVD Test", producer="Réalisateur", is_available=True, can_borrow=True)
    assert client.login(username="client", password="test1234")

    response = client.get(reverse("client:espace_client"))
    assert "DVD Test" in response.content.decode()
    assert dvd.media_type == "dvd"


@pytest.mark.django_db
def test_cdclient_creation_and_display(client, client_user):
    cd = CDClient.objects.create(name="CD Test", artist="Artiste", is_available=True, can_borrow=True)
    assert client.login(username="client", password="test1234")

    response = client.get(reverse("client:espace_client"))
    assert "CD Test" in response.content.decode()
    assert cd.media_type == "cd"


@pytest.mark.django_db
def test_boardgameclient_not_in_available_media(client, client_user):
    board_game = BoardGameClient.objects.create(name="Jeu Test", creators="Créateur", is_visible=True)
    assert client.login(username="client", password="test1234")

    response = client.get(reverse("client:espace_client"))
    assert "Jeu Test" not in response.content.decode()
    assert board_game.media_type == "board_game"
