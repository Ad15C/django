import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user():
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='12345StrongPass!'
    )
    return user


@pytest.fixture
def staff_user():
    user = get_user_model().objects.create_user(
        username='staffuser',
        email='staffuser@example.com',
        password='staffpassword',
        is_staff=True,
        is_active=True
    )
    return user


@pytest.fixture
def client_user():
    user = get_user_model().objects.create_user(
        username='clientuser',
        email='clientuser@example.com',
        password='clientpassword',
        is_active=True
    )
    return user


# Exemple de test avec la marque django_db
@pytest.mark.django_db
def test_user_creation(user):
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'


# Exemple de test avec la marque django_db
@pytest.mark.django_db
def test_user_creation(user, db):
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
