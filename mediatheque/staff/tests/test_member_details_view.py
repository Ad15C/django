import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from bs4 import BeautifulSoup

User = get_user_model()


@pytest.mark.django_db
def test_member_detail_view(client):
    # Création d’un utilisateur staff avec la permission
    user = User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='password123',
        is_staff=True,
        is_active=True
    )

    # Ajouter la permission AVANT le login
    permission = Permission.objects.get(
        codename='can_view_members',
        content_type__app_label='authentification'
    )
    user.user_permissions.add(permission)
    user.refresh_from_db()

    client.login(username='staffuser', password='password123')

    member = User.objects.create_user(
        username='testmember',
        email='jean.dupont@example.com',
        first_name='Jean',
        last_name='Dupont',
        password='fakepass123',
        is_staff=False,
        is_active=True
    )

    url = reverse('staff:membre_detail', args=[member.pk])
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()

    assert 'Détails du Membre' in content
    assert 'Jean' in content
    assert 'Dupont' in content
    assert 'testmember' in content
    assert 'jean.dupont@example.com' in content
    assert 'Actif' in content
    assert 'Non' in content  # Staff = Non

    assert reverse('staff:liste_membres') in content
    assert 'Retour à la liste' in content
    assert reverse('staff:espace_staff') in content

    soup = BeautifulSoup(response.content, 'html.parser')
    assert soup.find('a', href=reverse('staff:liste_membres'))
    assert soup.find('a', href=reverse('staff:espace_staff'))


@pytest.mark.django_db
def test_redirect_when_pk_zero(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass',
        is_staff=True
    )

    permission = Permission.objects.get(
        codename='can_view_members',
        content_type__app_label='authentification'
    )
    user.user_permissions.add(permission)
    user.refresh_from_db()

    client.login(username='admin', password='adminpass')

    response = client.get(reverse('staff:membre_detail', args=[0]))
    assert response.status_code == 302
    assert reverse('staff:liste_membres') in response.url


def test_member_detail_requires_login(client):
    response = client.get(reverse('staff:membre_detail', args=[1]))
    assert response.status_code == 302  # redirect to login


@pytest.mark.django_db
def test_member_detail_permission_denied(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='simpleuser',
        email='simple@example.com',
        password='pass',
        is_staff=True
    )

    # Pas de permission ajoutée ici

    client.login(username='simpleuser', password='pass')
    response = client.get(reverse('staff:membre_detail', args=[1]))
    assert response.status_code == 403  # permission denied
