import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from staff.models import StaffBorrowItem, MediaStaff, BookStaff
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
        available=True,
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

    # Créer un objet MediaStaff (par exemple un livre)
    media_item = MediaStaff.objects.create(name="Book 1", media_type="book", available=True)

    # Créer un emprunt pour cet utilisateur
    borrow_item = StaffBorrowItem.objects.create(user=user, media=media_item, is_returned=False)

    # Se connecter avec cet utilisateur
    client.login(username='client', password='password')

    # Récupérer la réponse de la vue client_dashboard
    response = client.get(reverse('authentification:espace_client'))

    # Afficher les emprunts pour déboguer
    print("Emprunts dans le test : ", StaffBorrowItem.objects.filter(user=user))

    # Vérifier le contenu de la réponse pour déboguer
    print(response.content.decode())  # Afficher le contenu de la réponse pour vérifier

    # Vérifier que le message "Aucune réservation en cours." n'est pas dans la réponse
    assert 'Aucune réservation en cours.' not in response.content.decode()

    # Vérifier que le nom de l'élément emprunté est bien présent dans la réponse
    assert media_item.name in response.content.decode()


@pytest.mark.django_db
def test_access_denied_for_non_client(client, staff_user):
    client.login(username='staffuser', password='staffpass123')
    url = reverse('authentification:espace_client')
    response = client.get(url)

    # Si ton décorateur @role_required redirige, vérifie cela
    assert response.status_code in (403, 302)
