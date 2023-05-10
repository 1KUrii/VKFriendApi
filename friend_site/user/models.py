from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=150, blank=False,
                              null=False)
    username = models.CharField(unique=True, max_length=150, blank=False,
                                null=False)
    password = models.CharField(max_length=150, blank=False, null=False)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
