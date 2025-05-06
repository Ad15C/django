import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from staff.models import StaffBorrowItem, BookStaff, BoardGameStaff, CDStaff, DVDStaff
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_staff_dashboard(client):
    # Création d'un utilisateur staff et connexion
    staff_user = User.objects.create_user(username="staffuser", password="testpass", role=User.STAFF)
    client.login(username="staffuser", password="testpass")

    # Création de plusieurs médias de chaque type : Livre, CD, DVD, et Board Game
    book1 = BookStaff.objects.create(name="Book 1", author="Author 1", available=True, can_borrow=True)
    book2 = BookStaff.objects.create(name="Book 2", author="Author 2", available=True, can_borrow=True)
    cd1 = CDStaff.objects.create(name="CD 1", artist="Artist 1", is_available=True,
                                 can_borrow=True)  # Utiliser is_available ici
    cd2 = CDStaff.objects.create(name="CD 2", artist="Artist 2", is_available=True,
                                 can_borrow=True)  # Utiliser is_available ici
    dvd1 = DVDStaff.objects.create(name="DVD 1", producer="Producer 1", is_available=True,
                                   can_borrow=True)  # Utiliser is_available ici
    dvd2 = DVDStaff.objects.create(name="DVD 2", producer="Producer 2", is_available=True,
                                   can_borrow=True)  # Utiliser is_available ici
    board_game1 = BoardGameStaff.objects.create(name="Board Game 1", creators="Creator 1", is_available=True,
                                                can_borrow=False)
    board_game2 = BoardGameStaff.objects.create(name="Board Game 2", creators="Creator 2", is_available=True,
                                                can_borrow=False)

    # Emprunts actifs (dans les temps)
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=book1,
        is_returned=False,
        due_date=timezone.now() + timedelta(days=3)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=cd1,
        is_returned=False,
        due_date=timezone.now() + timedelta(days=5)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=dvd1,
        is_returned=False,
        due_date=timezone.now() + timedelta(days=7)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=board_game1,
        is_returned=False,
        due_date=timezone.now() + timedelta(days=4)
    )

    # Emprunts en retard
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=book2,
        is_returned=False,
        due_date=timezone.now() - timedelta(days=3)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=cd2,
        is_returned=False,
        due_date=timezone.now() - timedelta(days=2)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=dvd2,
        is_returned=False,
        due_date=timezone.now() - timedelta(days=1)
    )
    StaffBorrowItem.objects.create(
        user=staff_user,
        media=board_game2,
        is_returned=False,
        due_date=timezone.now() - timedelta(days=4)
    )

    # Appel de la vue
    response = client.get(reverse('authentification:espace_staff'))

    # Vérifie que le code de statut de la réponse est 200
    assert response.status_code == 200
    content = response.content.decode()

    # Vérifie que les médias sont présents dans la réponse HTML
    assert "Book 1" in content  # emprunt actif
    assert "Book 2" in content  # emprunt en retard
    assert "CD 1" in content  # emprunt actif
    assert "CD 2" in content  # emprunt en retard
    assert "DVD 1" in content  # emprunt actif
    assert "DVD 2" in content  # emprunt en retard
    assert "Board Game 1" in content  # emprunt actif
    assert "Board Game 2" in content  # emprunt en retard
