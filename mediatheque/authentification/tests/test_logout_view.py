import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client


@pytest.mark.django_db
def test_logout_view_redirects_to_login(client: Client, user: User):
    # Log in the user first
    client.login(username=user.username, password='password')

    # Send GET request to the logout view
    response = client.get(reverse('authentification:deconnexion'))

    # Assert the redirect to the login page
    assert response.status_code == 302
    assert response.url == reverse('authentification:connexion')


@pytest.mark.django_db
def test_logout_view_shows_success_message(client: Client, user: User):
    # Log in the user first
    client.login(username=user.username, password='password')

    # Send GET request to the logout view
    response = client.get(reverse('authentification:deconnexion'))

    # Check if the success message is present
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].message == "Vous êtes maintenant déconnecté."
    assert messages[0].level == 25  # Success level in Django is 25


@pytest.mark.django_db
def test_logout_view_when_not_logged_in(client: Client):
    # Access the logout page without being logged in
    response = client.get(reverse('authentification:deconnexion'))

    # The user should be redirected to the login page even if not logged in
    assert response.status_code == 302
    assert response.url == reverse('authentification:connexion')
