import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client


@pytest.mark.django_db
def test_login_view_get():
    """
    Test que la vue de connexion affiche le formulaire.
    """
    client = Client()
    response = client.get(reverse('mediatheque.authentification:connexion'))

    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_login_view_post_valid_credentials():
    """
    Test que l'utilisateur peut se connecter avec des identifiants valides.
    """
    User = get_user_model()
    # Ajout de l'email obligatoire
    user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123',
                                    role=User.CLIENT)

    client = Client()
    response = client.post(reverse('mediatheque.authentification:connexion'),
                           {'username': 'testuser', 'password': 'password123'})

    # Vérifier la redirection vers l'espace client
    assert response.status_code == 302
    assert response.url == reverse('mediatheque.authentification:espace_client')

    # Vérifier si le message de succès est affiché
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].message == "Vous êtes connecté avec succès."


@pytest.mark.django_db
def test_login_view_post_invalid_credentials():
    """
    Test que l'utilisateur reçoit un message d'erreur pour des identifiants invalides.
    """
    User = get_user_model()
    # Ajout de l'email obligatoire
    User.objects.create_user(username='testuser', email='testuser@example.com', password='password123',
                             role=User.CLIENT)

    client = Client()
    response = client.post(reverse('mediatheque.authentification:connexion'),
                           {'username': 'testuser', 'password': 'wrongpassword'})

    # Vérifier que la connexion échoue et que l'erreur est affichée dans les messages
    assert response.status_code == 200  # Il devrait rester sur la page de connexion
    assert "Nom d'utilisateur ou mot de passe incorrect." in [str(message) for message in
                                                              get_messages(response.wsgi_request)]


@pytest.mark.django_db
def test_login_redirect_for_staff_user():
    """
    Test la redirection vers l'espace staff pour un utilisateur avec le rôle STAFF.
    """
    User = get_user_model()
    # Ajout de l'email obligatoire
    staff_user = User.objects.create_user(username='staffuser', email='staffuser@example.com', password='password123',
                                          role=User.STAFF)

    client = Client()
    response = client.post(reverse('mediatheque.authentification:connexion'),
                           {'username': 'staffuser', 'password': 'password123'})

    # Vérifier la redirection vers l'espace staff
    assert response.status_code == 302
    assert response.url == reverse('mediatheque.authentification:espace_staff')


@pytest.mark.django_db
def test_login_redirect_for_admin_user():
    """
    Test la redirection vers l'espace admin pour un utilisateur avec le rôle ADMIN.
    """
    User = get_user_model()
    # Ajout de l'email obligatoire
    admin_user = User.objects.create_user(username='adminuser', email='adminuser@example.com', password='password123',
                                          role=User.ADMIN)

    client = Client()
    response = client.post(reverse('mediatheque.authentification:connexion'),
                           {'username': 'adminuser', 'password': 'password123'})

    # Vérifier la redirection vers l'interface d'administration
    assert response.status_code == 302
    assert response.url == '/admin/'
