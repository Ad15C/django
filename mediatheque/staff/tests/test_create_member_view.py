import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from mediatheque.authentification.models import CustomUser


@pytest.mark.django_db
def test_create_member_get(client):
    user = CustomUser.objects.create_user(
        email='user1@example.com',
        username='user1',
        password='pass123',
        is_staff=True
    )
    permission = Permission.objects.get(codename='can_add_member')
    user.user_permissions.add(permission)
    client.force_login(user)

    url = reverse('staff:creer_membre')
    response = client.get(url)

    content = response.content.decode('utf-8')  # Décodage du contenu bytes en string
    assert response.status_code == 200
    assert 'Créer un Membre' in content


@pytest.mark.django_db
def test_create_member_post_valid(client):
    user = CustomUser.objects.create_user(
        email='admin@example.com',
        username='admin',
        password='adminpass123',
        is_staff=True
    )
    permission = Permission.objects.get(codename='can_add_member')
    user.user_permissions.add(permission)
    client.force_login(user)

    url = reverse('staff:creer_membre')
    data = {
        'username': 'newmember',
        'email': 'newmember@example.com',
        'password1': 'StrongPass!123',
        'password2': 'StrongPass!123',
    }
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('staff:liste_membres')

    assert CustomUser.objects.filter(email='newmember@example.com', username='newmember').exists()


@pytest.mark.django_db
def test_create_member_post_invalid(client):
    user = CustomUser.objects.create_user(
        email='user3@example.com',
        username='user3',
        password='pass123',
        is_staff=True
    )
    permission = Permission.objects.get(codename='can_add_member')
    user.user_permissions.add(permission)
    client.force_login(user)

    url = reverse('staff:creer_membre')
    data = {
        'username': '',  # invalide car vide
        'email': '',  # invalide aussi
    }
    response = client.post(url, data)

    content = response.content.decode('utf-8')
    assert response.status_code == 200
    assert 'Erreur lors de la création du membre' in content


@pytest.mark.django_db
def test_create_member_permission_denied(client):
    user = CustomUser.objects.create_user(
        email='user4@example.com',
        username='user4',
        password='pass123',
        is_staff=True
    )
    # Pas de permission ajoutée volontairement
    client.force_login(user)

    url = reverse('staff:creer_membre')
    response = client.get(url)

    assert response.status_code == 403

@pytest.mark.django_db
def test_create_member_get_buttons(client):
    user = CustomUser.objects.create_user(
        email='user1@example.com',
        username='user1',
        password='pass123',
        is_staff=True
    )
    permission = Permission.objects.get(codename='can_add_member')
    user.user_permissions.add(permission)
    client.force_login(user)

    url = reverse('staff:creer_membre')
    response = client.get(url)
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'Créer un Membre' in content

    # Vérifie la présence du bouton submit
    assert '<button type="submit"' in content
    assert 'Créer le membre' in content

    # Vérifie la présence du lien "Retour à la liste"
    liste_url = reverse('staff:liste_membres')
    assert f'<a href="{liste_url}"' in content
    assert 'Retour à la liste' in content
