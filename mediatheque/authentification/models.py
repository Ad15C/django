from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    STAFF = 'staff'
    CLIENT = 'client'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (STAFF, 'Staff'),
        (CLIENT, 'Client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CLIENT)

    def __str__(self):
        return self.username

    @property
    def is_staff_user(self):
        return self.role == self.STAFF

    @property
    def is_client_user(self):
        return self.role == self.CLIENT

    @property
    def is_admin_user(self):
        return self.role == self.ADMIN
