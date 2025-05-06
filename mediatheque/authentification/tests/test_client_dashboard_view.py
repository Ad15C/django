import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from staff.models import StaffBorrowItem, MediaStaff, BookStaff, BoardGameStaff, CDStaff, DVDStaff
from django.utils import timezone


@pytest.mark.django_db
def test_client_dashboard_access(client):
    # Créer un utilisateur
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='A7#fK!x92q'
    )

    # Connecter l'utilisateur
    client.login(username='testuser', password='A7#fK!x92q')

    # Créer un objet MediaStaff (exemple avec BookStaff ici)
    media = BookStaff.objects.create(
        name="Test Book",
        author="Author Name",
        available=True,  # Assurez-vous que ce champ existe
        can_borrow=True
    )

    # Créer un emprunt pour cet utilisateur
    borrow_item = StaffBorrowItem.objects.create(
        user=user,
        media=media,
        is_returned=False,
        borrow_date=timezone.now(),
        due_date=timezone.now() + timezone.timedelta(days=7)
    )

    # Accéder à l'espace client
    url = reverse('authentification:espace_client')
    response = client.get(url)

    # Vérifier la réponse
    assert response.status_code == 200
    assert 'Bienvenue' in response.content.decode()  # Assurer que le message de bienvenue est présent


@pytest.mark.django_db
def test_client_dashboard_with_data(client):
    # Créer un utilisateur client
    user = get_user_model().objects.create_user(username='client', password='password')

    # Créer un objet BoardGameStaff avec les champs valides
    media_item = BoardGameStaff.objects.create(
        name="Test Board Game",
        creators="Creator Name",
        is_available=True,
        game_type="Strategy",
    )

    # Créer un emprunt pour cet utilisateur
    borrow_item = StaffBorrowItem.objects.create(user=user, media=media_item, is_returned=False)

    # Se connecter avec cet utilisateur
    client.login(username='client', password='password')

    # Récupérer la réponse de la vue client_dashboard
    response = client.get(reverse('authentification:espace_client'))

    # Vérifier que le message "Aucune réservation en cours." n'est pas dans la réponse
    assert 'Aucune réservation en cours.' not in response.content.decode()

    # Vérifier que le nom de l'élément emprunté est bien présent dans la réponse
    assert media_item.name in response.content.decode()


@pytest.mark.django_db
def test_access_denied_for_non_client(client, staff_user):
    # Connecter un utilisateur staff (qui ne doit pas avoir accès au tableau de bord client)
    client.login(username='staffuser', password='staffpass123')
    url = reverse('authentification:espace_client')
    response = client.get(url)

    # Si ton décorateur @role_required redirige, vérifier cela
    assert response.status_code in (403, 302)  # Vérifier si l'accès est interdit (403) ou redirigé (302)


@pytest.mark.django_db
def test_client_dashboard_with_board_game(client):
    # Créer un utilisateur client
    user = get_user_model().objects.create_user(username='client', password='password')

    # Créer un objet BoardGameStaff
    media_item = BoardGameStaff.objects.create(
        name="Test Board Game",
        creators="Creator Name",
        is_available=True,  # Hérédité de MediaStaff
        game_type="Strategy",
    )

    # Créer un emprunt pour cet utilisateur (bien que les jeux de plateau ne peuvent pas être empruntés)
    borrow_item = StaffBorrowItem.objects.create(user=user, media=media_item, is_returned=False)

    # Se connecter en tant qu'utilisateur client
    client.login(username='client', password='password')

    # Accéder au tableau de bord client
    response = client.get(reverse('authentification:espace_client'))

    # Vérifier que le nom de l'élément emprunté est bien présent dans la réponse
    assert media_item.name in response.content.decode()

    # Vérifier que le jeu de plateau n'est pas empruntable (car `can_borrow` est `False`)
    assert 'Emprunter' not in response.content.decode()  # Assurer que "Emprunter" n'est pas présent
