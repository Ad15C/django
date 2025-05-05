import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from staff.models import MediaStaff, StaffBorrowItem
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_staff_dashboard(client):
    # Création d'un utilisateur staff et connexion
    staff_user = User.objects.create_user(username="staffuser", password="testpass", role=User.STAFF)
    client.login(username="staffuser", password="testpass")

    # Création de plusieurs médias de chaque type : Livre, CD, DVD, et Board Game
    book1 = MediaStaff.objects.create(name="Book 1", media_type="book", available=True, can_borrow=True)
    book2 = MediaStaff.objects.create(name="Book 2", media_type="book", available=True, can_borrow=True)
    cd1 = MediaStaff.objects.create(name="CD 1", media_type="cd", available=True, can_borrow=True)
    cd2 = MediaStaff.objects.create(name="CD 2", media_type="cd", available=True, can_borrow=True)
    dvd1 = MediaStaff.objects.create(name="DVD 1", media_type="dvd", available=True, can_borrow=True)
    dvd2 = MediaStaff.objects.create(name="DVD 2", media_type="dvd", available=True, can_borrow=True)
    board_game1 = MediaStaff.objects.create(name="Board Game 1", media_type="board_game", available=True,
                                            can_borrow=True)
    board_game2 = MediaStaff.objects.create(name="Board Game 2", media_type="board_game", available=True,
                                            can_borrow=True)

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
