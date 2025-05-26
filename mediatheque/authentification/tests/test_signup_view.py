import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


@pytest.mark.django_db
def test_signup_success(client):
    """Test de l'inscription réussie"""
    url = reverse('authentification:inscription')

    # Déconnexion de l'utilisateur s'il est déjà connecté
    client.logout()

    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'A7#fK!x92q',
        'password2': 'A7#fK!x92q',
        'role': 'client',
    }

    response = client.post(url, data)

    # Vérifie que la réponse est une redirection (302) après une inscription réussie
    assert response.status_code == 302  # Vérifie que la redirection a lieu
    assert response.url == reverse('authentification:home')  # Vérifie que la redirection est vers la page d'accueil

    # Vérifie que l'utilisateur a été créé et est bien connecté
    user = get_user_model().objects.get(username='newuser')
    assert user is not None  # Vérifie que l'utilisateur existe dans la base de données
    assert user.is_authenticated  # Vérifie que l'utilisateur est authentifié après l'inscription

    # Vérifie que la session contient l'utilisateur connecté
    assert '_auth_user_id' in client.session

    # Vérifie que des messages de succès ont été envoyés
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) > 0
    assert "Inscription réussie ! Vous êtes maintenant connecté." in [msg.message for msg in messages]


@pytest.mark.django_db
def test_signup_password_strength(client):
    """Test de validation de la longueur du mot de passe"""
    url = reverse('authentification:inscription')

    # Données avec un mot de passe trop court
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'abc',
        'password2': 'abc',
        'role': 'client',
    }

    response = client.post(url, data)

    # Vérifie que la réponse est 200 (formulaire avec erreurs)
    assert response.status_code == 200

    # Vérifie que l'erreur de validation du mot de passe est dans la réponse HTML
    assert 'Le mot de passe doit contenir au moins 6 caractères.' in response.content.decode()


@pytest.mark.django_db
def test_signup_invalid_passwords(client):
    """Test que l'inscription échoue si les mots de passe ne correspondent pas"""
    url = reverse('authentification:inscription')

    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'A7#fK!x92q',
        'password2': 'notthesame',
        'role': 'client',
    }

    response = client.post(url, data)

    # Vérifier que la réponse est un code 200 (formulaire avec erreurs)
    assert response.status_code == 200

    # Vérifier qu'il y a une erreur indiquant que les mots de passe ne correspondent pas
    assert 'Les mots de passe ne correspondent pas.' in response.content.decode()
