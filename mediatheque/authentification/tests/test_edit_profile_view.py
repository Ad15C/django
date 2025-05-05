import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


@pytest.fixture
def user(db):
    """Fixture pour créer un utilisateur pour les tests"""
    user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
    return user


@pytest.mark.django_db
def test_edit_profile_valid_data(client, user):
    """Test de la mise à jour du profil avec des données valides"""
    client.login(username=user.username, password='password123')

    # Données valides pour mettre à jour le profil
    data = {
        'username': 'nouveau_username',
        'email': 'nouveauemail@example.com',
        'password': '',  # Aucun mot de passe, juste la mise à jour du profil
    }

    # Envoi de la requête POST pour modifier le profil
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.post(url, data)

    # Vérifier que la redirection a eu lieu
    assert response.status_code == 302  # Redirection après une mise à jour réussie
    assert response.url == reverse('authentification:modifier_profil', args=[user.id])

    # Vérifier que les données utilisateur ont bien été mises à jour
    user.refresh_from_db()
    assert user.username == 'nouveau_username'
    assert user.email == 'nouveauemail@example.com'


@pytest.mark.django_db
def test_edit_profile_get(client, user):
    """Test pour vérifier que la vue affiche correctement le formulaire"""
    client.login(username=user.username, password='password123')

    # Accéder à la page de modification de profil
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.get(url)

    # Vérifier que la réponse est correcte
    assert response.status_code == 200
    assert 'Modifier le profil' in response.content.decode()  # Assurer que le titre est bien affiché


@pytest.mark.django_db
def test_edit_profile_with_password(client, user):
    """Test pour vérifier que le mot de passe est mis à jour correctement"""
    client.login(username=user.username, password='password123')

    # Données valides avec un mot de passe modifié
    data = {
        'username': 'nouveau_username',
        'email': 'nouveauemail@example.com',
        'password': 'nouveaupassword123',
    }

    # Envoi de la requête POST pour modifier le profil
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.post(url, data)

    # Vérifier que la redirection a eu lieu
    assert response.status_code == 302  # Redirection après une mise à jour réussie
    assert response.url == reverse('authentification:modifier_profil', args=[user.id])

    # Vérifier que le mot de passe de l'utilisateur a été mis à jour
    user.refresh_from_db()
    assert user.check_password('nouveaupassword123')


@pytest.mark.django_db
def test_edit_profile_invalid_data(client, user):
    """Test pour vérifier que le formulaire ne soumet pas les données invalides"""
    client.login(username=user.username, password='password123')

    # Données invalides (mot de passe trop court)
    data = {
        'username': 'nouveau_username',
        'email': 'nouveauemail@example.com',
        'password': '123',  # Mot de passe trop court
    }

    # Envoi de la requête POST pour modifier le profil
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.post(url, data)

    # Vérifier que la page est rendue à nouveau avec des erreurs de validation
    assert response.status_code == 200
    assert 'Le mot de passe doit contenir au moins 6 caractères.' in response.content.decode()


@pytest.mark.django_db
def test_edit_profile_no_password_change(client, user):
    """Test pour vérifier que le mot de passe ne change pas s'il n'est pas fourni"""
    client.login(username=user.username, password='password123')

    # Données sans mot de passe
    data = {
        'username': 'nouveau_username',
        'email': 'nouveauemail@example.com',
        'password': '',  # Aucun mot de passe
    }

    # Envoi de la requête POST pour modifier le profil
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.post(url, data)

    # Vérifier que la redirection a eu lieu
    assert response.status_code == 302  # Redirection après une mise à jour réussie

    # Vérifier que le mot de passe n'a pas changé
    user.refresh_from_db()
    assert user.check_password('password123')  # Le mot de passe doit être inchangé


@pytest.mark.django_db
def test_edit_profile_not_logged_in(client, user):
    """Test pour vérifier qu'un utilisateur non connecté est redirigé vers la connexion"""
    # Accéder à la page de modification de profil sans être connecté
    url = reverse('authentification:modifier_profil', args=[user.id])
    response = client.get(url)

    # Vérifier que l'utilisateur est redirigé vers la page de connexion avec le paramètre next
    assert response.status_code == 302
    assert '/auth/login/?next=' in response.url  # Vérifie que la redirection contient le paramètre `next`
    assert f'/auth/modifier_profil/{user.id}/' in response.url  # Vérifie que le `next` est correct
