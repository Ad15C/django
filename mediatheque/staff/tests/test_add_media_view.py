import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from mediatheque.staff.models import BookStaff, DVDStaff, CDStaff, BoardGameStaff
from mediatheque.authentification.models import CustomUser

User = get_user_model()


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='password123'
    )
    user.role = User.STAFF
    user.is_staff = True
    perm = Permission.objects.get(codename='can_add_media')
    user.user_permissions.add(perm)
    user.save()
    return user


@pytest.mark.django_db
def test_add_media_get_authenticated(client, staff_user):
    client.login(username='staff', password='password123')
    url = reverse('staff:ajouter_media')
    response = client.get(url)

    assert response.status_code == 200
    assert "Ajouter un Média".encode('utf-8') in response.content


@pytest.mark.django_db
@pytest.mark.parametrize("media_type,model,form_data", [
    ('book', BookStaff, {'name': 'Test Book', 'author': 'Author', 'isbn': '1234567890'}),
    ('dvd', DVDStaff, {'name': 'Test DVD', 'producer': 'Producer', 'duration': 120}),
    ('cd', CDStaff, {'name': 'Test CD', 'artist': 'Artist', 'track_count': 10}),
    ('board_game', BoardGameStaff, {'name': 'Test Game', 'creators': 'Publisher', 'players_min': 2, 'players_max': 4}),
])
def test_add_media_post_valid(client, staff_user, media_type, model, form_data):
    client.login(username='staff', password='password123')
    url = reverse('staff:ajouter_media')

    data = {'media_type': media_type}
    data.update(form_data)

    response = client.post(url, data, follow=True)

    # Vérifie la redirection après la soumission du formulaire
    if response.status_code == 200:
        # Si le code de status est 200, cela signifie que la page a été rendue sans redirection
        assert response.context['form'].errors  # Vérifie si le formulaire a des erreurs
    else:
        # Si la redirection a eu lieu, vérifier la redirection vers la bonne URL
        assert response.redirect_chain[0][0].endswith(reverse('staff:media_liste'))

    # Vérifie la création de l'objet dans la base de données
    assert model.objects.filter(name=form_data['name']).exists()


@pytest.mark.django_db
def test_add_media_post_invalid_type(client, staff_user):
    client.login(username='staff', password='password123')
    url = reverse('staff:ajouter_media')
    response = client.post(url, {'media_type': 'invalid_type'}, follow=True)

    # Vérifie qu'on reste sur la page et qu'on a un message d'erreur
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("Type de média invalide" in str(m) for m in messages)


@pytest.mark.django_db
def test_add_media_post_invalid_form(client, staff_user):
    client.login(username='staff', password='password123')
    url = reverse('staff:ajouter_media')
    response = client.post(url, {'media_type': 'book', 'title': ''}, follow=True)

    # On reste sur la page (erreur dans le formulaire)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("Erreur lors de l'ajout du média" in str(m) for m in messages)
