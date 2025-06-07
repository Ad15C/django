import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from mediatheque.authentification.models import CustomUser


@pytest.fixture
def staff_user_with_permission(db):
    """
    Crée un utilisateur staff avec la permission de mise à jour.
    """
    user = CustomUser.objects.create_user(
        email='staff@example.com',
        username='staffuser',
        password='pass123',
        is_staff=True,
        role='staff',
    )
    permission = Permission.objects.get(codename='can_update_member')
    user.user_permissions.add(permission)
    return user


@pytest.mark.django_db
def test_update_member_get(client, staff_user_with_permission):
    """
    Teste l'accès GET à la page de modification d'un membre.
    """
    client.force_login(staff_user_with_permission)
    url = reverse('staff:modifier_membre', args=[staff_user_with_permission.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert b"Modifier un Membre" in response.content


@pytest.mark.django_db
def test_update_member_post_success(client, staff_user_with_permission):
    """
    Teste une mise à jour réussie du membre sans modifier le mot de passe.
    """
    client.force_login(staff_user_with_permission)
    url = reverse('staff:modifier_membre', args=[staff_user_with_permission.pk])

    data = {
        "username": "nouveau_nom",
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "nouveau@mail.com",
        "is_staff": True,
        "is_active": True,
    }

    response = client.post(url, data)
    staff_user_with_permission.refresh_from_db()

    assert response.status_code == 302  # redirection après succès
    assert staff_user_with_permission.username == "nouveau_nom"
    assert staff_user_with_permission.email == "nouveau@mail.com"
    assert staff_user_with_permission.first_name == "Jean"
    assert staff_user_with_permission.last_name == "Dupont"


@pytest.mark.django_db
def test_update_member_post_invalid_email(client, staff_user_with_permission):
    client.force_login(staff_user_with_permission)
    url = reverse('staff:modifier_membre', args=[staff_user_with_permission.pk])

    data = {
        "username": "nom_ok",
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "invalide",  # email invalide
        "is_staff": True,
        "is_active": True,
    }

    response = client.post(url, data)
    content = response.content.decode()
    print(content)  # Affiche le HTML complet rendu

    assert response.status_code == 200
    assert (
            "Entrez une adresse email valide." in content
            or "Enter a valid email address." in content
            or "Saisissez une adresse de courriel valide." in content
    )


@pytest.mark.django_db
def test_update_member_permission_denied(client, django_user_model):
    """
    Vérifie qu'un utilisateur sans permission ne peut pas accéder à la page de modification.
    """
    user = django_user_model.objects.create_user(
        username='normal',
        password='pass1234',
        email='normal@example.com'
    )
    client.force_login(user)
    url = reverse('staff:modifier_membre', args=[user.pk])
    response = client.get(url)

    assert response.status_code == 403  # accès refusé
