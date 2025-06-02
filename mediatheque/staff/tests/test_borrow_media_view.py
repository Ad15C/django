import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from mediatheque.staff.models import MediaStaff, BoardGameStaff, StaffBorrowItem
from mediatheque.staff.forms import BorrowMediaForm
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
    perm = Permission.objects.get(codename='can_borrow_media')
    user.user_permissions.add(perm)
    user.save()
    return user


@pytest.fixture
def media_item(db):
    return MediaStaff.objects.create(name='Test Media', is_available=True)


@pytest.fixture
def board_game(db):
    return BoardGameStaff.objects.create(name='BoardGameTest', is_available=True)


@pytest.fixture
def media_available(db):
    return MediaStaff.objects.create(name='MediaTest', is_available=True)


@pytest.fixture
def unavailable_media(db):
    return MediaStaff.objects.create(name='Unavailable Media', is_available=False)


def test_clean_media_valid(staff_user, media_available):
    due_date_str = make_due_date(3)
    form = BorrowMediaForm(
        data={'media': media_available.pk, 'due_date': due_date_str},
        user=staff_user
    )
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_clean_media_not_borrowable(staff_user, media_available):
    board_game = BoardGameStaff.objects.create(name="Mon Jeu", is_available=True)
    form = BorrowMediaForm(data={'media': board_game.pk, 'due_date': '2025-05-21'}, user=staff_user)
    assert not form.is_valid()
    assert any("Vous n\'êtes pas autorisé à emprunter le média" in e for e in form.errors.get('media', []))


@pytest.mark.django_db
def test_clean_media_unavailable(staff_user, unavailable_media):
    form = BorrowMediaForm(data={'media': unavailable_media.pk, 'due_date': '2025-05-21'}, user=staff_user)
    assert not form.is_valid()
    assert f"Le média {unavailable_media.name} n\'est pas disponible pour emprunt." in form.errors['media']


@pytest.mark.django_db
def test_clean_media_board_game(staff_user, board_game):
    form = BorrowMediaForm(data={'media': board_game.pk, 'due_date': '2025-05-21'}, user=staff_user)
    assert not form.is_valid()
    assert 'media' in form.errors
    assert any("Vous n\'êtes pas autorisé à emprunter le média" in e for e in form.errors['media'])


@pytest.fixture
def overdue_borrow_item(staff_user, media_item):
    borrow_date = timezone.now() - timedelta(days=10)
    due_date = timezone.now() - timedelta(days=5)
    return StaffBorrowItem.objects.create(
        user=staff_user,
        media=media_item,
        borrow_date=borrow_date,
        due_date=due_date,
        is_returned=False
    )


@pytest.fixture
def create_active_borrows():
    def _create(user, count):
        for i in range(count):
            media = MediaStaff.objects.create(name=f'Media {i}', is_available=True)
            StaffBorrowItem.objects.create(
                user=user,
                media=media,
                borrow_date=timezone.now(),
                due_date=timezone.now() + timedelta(days=7),
                is_returned=False
            )

    return _create


@pytest.mark.django_db
def test_borrow_media_with_board_game(staff_user, board_game, client):
    url = reverse('staff:emprunter', kwargs={'pk': board_game.pk})
    client.login(username='staff', password='password123')
    response = client.get(url, follow=False)
    assert response.status_code == 302
    assert response.url == reverse('staff:media_liste')
    response = client.get(response.url)
    messages = list(get_messages(response.wsgi_request))
    assert any("Les jeux de société ne peuvent pas être empruntés." in m.message for m in messages)


@pytest.mark.django_db
def test_check_borrowing_conditions_with_overdue(client, staff_user, overdue_borrow_item):
    overdue_borrow_item.due_date = timezone.now() - timedelta(days=1)
    overdue_borrow_item.save()
    client.login(username=staff_user.username, password='password123')
    response = client.get(reverse('staff:emprunter', args=[1]), follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) > 0
    assert any('Vous avez des emprunts en retard' in m.message for m in messages)


@pytest.mark.django_db
def test_borrow_media_limit_reached(staff_user, media_item, client, create_active_borrows):
    create_active_borrows(staff_user, 3)
    url = reverse('staff:emprunter', kwargs={'pk': media_item.pk})
    client.login(username='staff', password='password123')
    due_date_str = make_due_date(7)
    response = client.post(url, data={'due_date': due_date_str}, follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) > 0
    assert any("Vous avez atteint la limite de 3 emprunts." in m.message for m in messages)


@pytest.mark.django_db
def test_successful_borrow_media(staff_user, media_item, client):
    url = reverse('staff:emprunter', kwargs={'pk': media_item.pk})
    client.login(username='staff', password='password123')
    due_date_str = make_due_date(7)
    response = client.post(url, data={
        'media': media_item.pk,
        'due_date': due_date_str
    })
    assert response.status_code == 302
    assert StaffBorrowItem.objects.filter(user=staff_user, media=media_item).exists()
    response = client.get(response.url)
    messages = list(get_messages(response.wsgi_request))
    assert any("emprunté avec succès" in m.message.lower() for m in messages)


@pytest.mark.django_db
def test_user_without_permission_cannot_borrow_media(staff_user, media_item, client):
    perm = Permission.objects.get(codename='can_borrow_media')
    staff_user.user_permissions.remove(perm)
    staff_user.save()
    url = reverse('staff:emprunter', kwargs={'pk': media_item.pk})
    client.login(username='staff', password='password123')
    due_date_str = make_due_date(7)
    response = client.post(url, data={'due_date': due_date_str})
    assert response.status_code == 403  # On attend un Forbidden



@pytest.mark.django_db
def test_check_borrowing_conditions_with_max_active_borrows(client, staff_user, media_available):
    for _ in range(3):
        StaffBorrowItem.objects.create(
            user=staff_user,
            media=media_available,
            borrow_date=timezone.now(),
            due_date=timezone.make_aware(datetime.combine((timezone.now() + timedelta(days=7)).date(), time.min)),
            is_returned=False
        )
    client.login(username=staff_user.username, password='password123')
    response = client.get(reverse('staff:emprunter', args=[media_available.pk]), follow=True)
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) > 0
    assert any('Vous avez atteint la limite de 3 emprunts.' in m.message for m in messages)


@pytest.mark.django_db
def test_borrow_media_with_past_due_date_invalid(staff_user, media_available):
    past_due_date = (timezone.now() - timedelta(days=1)).date().isoformat()
    form = BorrowMediaForm(
        data={'media': media_available.pk, 'due_date': past_due_date},
        user=staff_user
    )
    assert not form.is_valid()
    assert 'due_date' in form.errors
    assert "La date d\'échéance ne peut pas être dans le passé." in form.errors['due_date']


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login(client, media_item):
    url = reverse('staff:emprunter', kwargs={'pk': media_item.pk})
    response = client.get(url)
    login_url = reverse('mediatheque.authentification:connexion')
    assert response.status_code == 302
    assert response.url.startswith(login_url)
