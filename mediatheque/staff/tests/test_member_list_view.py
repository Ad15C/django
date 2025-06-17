import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from mediatheque.authentification.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def staff_user():
    content_type = ContentType.objects.get_for_model(User)
    permission, _ = Permission.objects.get_or_create(
        codename='can_view_members',
        name='Can view members',
        content_type=content_type,
    )

    user = User.objects.create_user(
        username='staff_user',
        email='staff@example.com',
        password='pass123',
        is_staff=True,
        role=User.STAFF,
        is_active=True,
    )
    user.user_permissions.add(permission)
    user.save()
    return user


@pytest.fixture
def client_logged(client, staff_user):
    client.force_login(staff_user)
    return client


@pytest.mark.django_db
def test_client_logged_access(client_logged):
    url = reverse('staff:liste_membres')
    response = client_logged.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_permission_required(client):
    url = reverse('staff:liste_membres')
    response = client.get(url)
    # Pas connecté = redirection vers login (302) ou 403
    assert response.status_code in [302, 403]


@pytest.mark.django_db
def test_member_list_view_access(client_logged):
    url = reverse('staff:liste_membres')
    response = client_logged.get(url)
    assert response.status_code == 200
    assert 'Liste des Membres' in response.content.decode()


@pytest.mark.django_db
def test_member_list_display(client_logged):
    CustomUser.objects.create_user(username='membre1', email='m1@example.com', password='pass', is_active=True)
    CustomUser.objects.create_user(username='membre2', email='m2@example.com', password='pass', is_active=False)

    url = reverse('staff:liste_membres')
    response = client_logged.get(url)

    content = response.content.decode()
    assert 'membre1' in content
    assert 'membre2' in content
    assert 'Actif' in content or 'Inactif' in content
    assert 'Modifier' in content
    assert 'Voir le détail' in content


@pytest.mark.django_db
def test_member_list_pagination(client, staff_user):
    User.objects.exclude(pk=staff_user.pk).delete()
    for i in range(15):
        User.objects.create_user(username=f'user{i}', email=f'u{i}@ex.com', password='pass')

    client.force_login(staff_user)
    url = reverse('staff:liste_membres')
    response = client.get(url)
    assert response.status_code == 200
    assert "Page 1 sur 2" in response.content.decode()

    response_page_2 = client.get(url + '?page=2')
    assert response_page_2.status_code == 200
    assert "Page 2 sur 2" in response_page_2.content.decode()


@pytest.mark.django_db
def test_no_members_found(client, staff_user):
    User.objects.exclude(pk=staff_user.pk).delete()

    client.force_login(staff_user)
    url = reverse('staff:liste_membres')
    response = client.get(url)
    assert response.status_code == 200
    assert "Aucun membre trouvé" in response.content.decode()


@pytest.mark.django_db
def test_delete_member_view(client):
    member = User.objects.create_user(username='testuser', email='testuser@example.com', password='pass123')

    staff_user = User.objects.create_user(
        username='staffuser',
        email='staffuser@example.com',
        password='staffpass',
        is_staff=True,
        role=User.STAFF,
    )

    content_type = ContentType.objects.get_for_model(User)
    perm_delete = Permission.objects.get(codename='can_delete_member', content_type=content_type)
    perm_view = Permission.objects.get(codename='can_view_members', content_type=content_type)
    staff_user.user_permissions.add(perm_delete, perm_view)
    staff_user.save()

    staff_user = User.objects.get(pk=staff_user.pk)
    client.force_login(staff_user)

    url = reverse('staff:supprimer_membre', args=[member.pk])

    response = client.get(url)
    assert response.status_code == 200
    assert "Confirmer la suppression" in response.content.decode('utf-8')

    response = client.post(url, follow=True)
    assert response.status_code == 200

    assert not User.objects.filter(pk=member.pk).exists()
    assert response.redirect_chain[-1][0] == reverse('staff:liste_membres')
    assert "Membre supprimé avec succès" in response.content.decode('utf-8')
