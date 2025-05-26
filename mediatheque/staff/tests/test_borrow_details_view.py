import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from mediatheque.staff.models import StaffBorrowItem, MediaStaff

User = get_user_model()


@pytest.mark.django_db
def test_borrow_detail_view_shows_only_borrowable_media(client):
    # Création utilisateur staff
    user = User.objects.create_user(
        username='staff_user',
        email='staff@example.com',
        password='password123',
        is_staff=True,
        role=User.STAFF
    )
    user.save()
    staff_group, _ = Group.objects.get_or_create(name='staff')
    user.groups.add(staff_group)

    permission = Permission.objects.get(codename='can_view_borrow')
    user.user_permissions.add(permission)
    user.save()

    logged_in = client.login(username='staff_user', password='password123')
    assert logged_in

    # Création médias
    book = MediaStaff.objects.create(name='Livre 1', media_type='Book')
    dvd = MediaStaff.objects.create(name='DVD 1', media_type='DVD')
    boardgame = MediaStaff.objects.create(name='Jeu de société', media_type='BoardGame')

    # Emprunt avec un média empruntable Book
    borrow_item_book = StaffBorrowItem.objects.create(
        user=user,
        media=book,
        due_date=timezone.now() + timezone.timedelta(days=7)
    )
    url = reverse('staff:detail_emprunt', kwargs={'pk': borrow_item_book.pk})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Livre 1' in content
    assert 'Jeu de société' not in content

    # Emprunt avec un média empruntable DVD
    borrow_item_dvd = StaffBorrowItem.objects.create(
        user=user,
        media=dvd,
        due_date=timezone.now() + timezone.timedelta(days=7)
    )
    url = reverse('staff:detail_emprunt', kwargs={'pk': borrow_item_dvd.pk})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert 'DVD 1' in content

    # Emprunt avec média non empruntable BoardGame
    borrow_item_boardgame = StaffBorrowItem.objects.create(
        user=user,
        media=boardgame,
        due_date=timezone.now() + timezone.timedelta(days=7)
    )
    url = reverse('staff:detail_emprunt', kwargs={'pk': borrow_item_boardgame.pk})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    # Le média non empruntable ne doit pas apparaître dans borrowable_media
    assert 'Jeu de société' not in content


@pytest.mark.django_db
def test_borrow_detail_view_with_multiple_emprunts(client):
    # Création utilisateur staff
    user = User.objects.create_user(
        username='staff_multi',
        email='multi@example.com',
        password='password123',
        is_staff=True,
        role=User.STAFF
    )
    user.save()
    staff_group, _ = Group.objects.get_or_create(name='staff')
    user.groups.add(staff_group)

    permission = Permission.objects.get(codename='can_view_borrow')
    user.user_permissions.add(permission)
    user.save()

    logged_in = client.login(username='staff_multi', password='password123')
    assert logged_in

    # Création médias
    book = MediaStaff.objects.create(name='Livre 1', media_type='Book')
    dvd = MediaStaff.objects.create(name='DVD 1', media_type='DVD')
    boardgame = MediaStaff.objects.create(name='Jeu de société', media_type='BoardGame')

    # Création d'un emprunt par média
    borrow_items = []
    for media_item in [book, dvd, boardgame]:
        borrow_items.append(
            StaffBorrowItem.objects.create(
                user=user,
                media=media_item,
                due_date=timezone.now() + timezone.timedelta(days=7)
            )
        )

    # Tester chaque emprunt séparément
    for borrow_item in borrow_items:
        url = reverse('staff:detail_emprunt', kwargs={'pk': borrow_item.pk})
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()

        if borrow_item.media.media_type in ['Book', 'DVD', 'CD']:
            assert borrow_item.media.name in content
        else:
            assert borrow_item.media.name not in content
