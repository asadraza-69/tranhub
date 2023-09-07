from __future__ import unicode_literals

from django.db import models
# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class AuthInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name='User *')
    secret_key = models.CharField(max_length=255)
    #ips = models.CharField(max_length=256, verbose_name='IPs')

    class Meta:
        db_table = u'auth_info'