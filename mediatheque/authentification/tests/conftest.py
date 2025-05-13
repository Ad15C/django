import os
import django
import pytest
from django.contrib.auth import get_user_model

# Assure-toi que Django est configuré avant tout
os.environ['DJANGO_SETTINGS_MODULE'] = 'mediatheque.settings'
django.setup()

# Fixture pour créer un utilisateur normal
@pytest.fixture
def user():
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='12345'
    )
    return user

# Fixture pour créer un utilisateur avec des droits de staff
@pytest.fixture
def staff_user():
    user = get_user_model().objects.create_user(
        username='staffuser',
        password='staffpassword',
        is_staff=True
    )
    return user

# Fixture pour créer un utilisateur client
@pytest.fixture
def client_user():
    user = get_user_model().objects.create_user(
        username='clientuser',
        password='clientpassword'
    )
    return user
