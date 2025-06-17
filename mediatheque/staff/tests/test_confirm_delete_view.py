import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def permission_delete_member():
    content_type = ContentType.objects.get_for_model(User)
    permission, _ = Permission.objects.get_or_create(
        codename='can_delete_member',
        name='Can delete member',
        content_type=content_type,
    )
    return permission


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username='staffuser',
        email='staffuser@example.com',
        password='pass123',
        is_staff=True,
        role=User.STAFF,
        is_active=True,
    )


@pytest.fixture
def staff_user_with_delete_permission(permission_delete_member):
    user = User.objects.create_user(
        username='staffuser2',
        email='staffuser2@example.com',
        password='pass123',
        is_staff=True,
        role=User.STAFF,
        is_active=True,
    )
    user.user_permissions.add(permission_delete_member)
    user.save()
    return user


@pytest.fixture
def member_to_delete():
    return User.objects.create_user(
        username='membertodelete',
        email='membertodelete@example.com',
        password='pass123',
        role=User.STAFF,
        is_active=True,
    )


@pytest.fixture
def client_logged_with_delete(client, staff_user_with_delete_permission):
    client.force_login(staff_user_with_delete_permission)
    return client


@pytest.mark.django_db
def test_delete_member_page_access(client_logged_with_delete, member_to_delete):
    url = reverse('staff:supprimer_membre', args=[member_to_delete.id])
    response = client_logged_with_delete.get(url)
    assert response.status_code == 200
    assert member_to_delete.username in response.content.decode()


@pytest.mark.django_db
def test_delete_member_post(client_logged_with_delete, member_to_delete):
    url = reverse('staff:supprimer_membre', args=[member_to_delete.id])
    response = client_logged_with_delete.post(url)
    assert response.status_code == 302
    assert response.url == reverse('staff:liste_membres')
    with pytest.raises(User.DoesNotExist):
        User.objects.get(id=member_to_delete.id)


@pytest.mark.django_db
def test_delete_member_forbidden_without_permission(client, staff_user, member_to_delete):
    client.force_login(staff_user)
    url = reverse('staff:supprimer_membre', args=[member_to_delete.id])
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_member_requires_login(client, member_to_delete):
    url = reverse('staff:supprimer_membre', args=[member_to_delete.id])
    response = client.get(url)
    assert response.status_code in [302, 403]
