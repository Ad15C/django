import pytest
from django.urls import reverse
from django.utils import timezone
from mediatheque.staff.models import StaffBorrowItem, BookStaff, CDStaff, DVDStaff, BoardGameStaff
from mediatheque.authentification.models import CustomUser


@pytest.mark.django_db
def test_staff_dashboard_authenticated_staff_user(client):
    # Créer un utilisateur staff avec un email
    user = CustomUser.objects.create_user(
        username='staffuser',
        email='staffuser@example.com',
        password='testpass'
    )
    user.role = CustomUser.STAFF  # Assurer que c'est un utilisateur staff en modifiant le champ 'role'
    user.save()

    # Connexion de l'utilisateur
    client.login(username='staffuser', password='testpass')

    # Créer des médias fictifs (books, cds, dvds, boardgames)
    BookStaff.objects.create(name='Book 1')
    CDStaff.objects.create(name='CD 1')
    DVDStaff.objects.create(name='DVD 1')
    BoardGameStaff.objects.create(name='BoardGame 1')

    # Créer un emprunt en cours
    StaffBorrowItem.objects.create(
        user=user,
        is_returned=False,
        due_date=timezone.now() + timezone.timedelta(days=7),
        media=BookStaff.objects.first()  # Associe un media
    )

    # Créer un emprunt en retard
    StaffBorrowItem.objects.create(
        user=user,
        is_returned=False,
        due_date=timezone.now() - timezone.timedelta(days=2),
        media=BookStaff.objects.first()  # Associe un media
    )

    # Appel de la vue
    url = reverse('staff:espace_staff')
    response = client.get(url)

    # Vérifications
    assert response.status_code == 200
    assert 'current_borrows' in response.context
    assert 'overdue_borrows' in response.context
    assert 'page_obj' in response.context

    # Vérifier le contenu retourné
    current_borrows = response.context['current_borrows']
    overdue_borrows = response.context['overdue_borrows']

    assert current_borrows.count() == 1
    assert overdue_borrows.count() == 1


@pytest.mark.django_db
def test_staff_dashboard_forbidden_for_non_staff_user(client):
    # Créer un utilisateur non-staff
    user = CustomUser.objects.create_user(username='regularuser', email='regularuser@example.com', password='testpass')
    user.role = CustomUser.CLIENT  # Assurer que c'est un utilisateur non-staff
    user.save()

    # Connexion de l'utilisateur
    client.login(username='regularuser', password='testpass')

    # Appel de la vue
    url = reverse('staff:espace_staff')  # Utiliser le bon nom d'URL
    response = client.get(url)

    # L'utilisateur non-staff doit recevoir une 403 Forbidden
    assert response.status_code == 403
