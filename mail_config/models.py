# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

_SEND_CHOICES = (('warning', 'Warning'), ('alerts', 'Alerts'), ('verification_code', 'Verification Code'))
_PORT_CHOICES = (('SSL', 'TLS/SSL'), ('StartTLS', 'STARTTLS'), ('None', 'None'))
TYPE_CHOICES = (('587', '587'), ('465', '465'), ('25', '25'))


class SendEmail(models.Model):
    title = models.CharField(max_length=128)
    email = models.EmailField(verbose_name = "Email *")
    password = models.CharField(max_length=128, verbose_name = "Password *")
    confirm_password = models.CharField(max_length=128, verbose_name = "Confirm Password *")
    host = models.CharField(max_length=128, verbose_name = "Host *")
    category = models.CharField(max_length=30, choices=_SEND_CHOICES,
                                unique=True, verbose_name = "Category *")
    port = models.CharField(max_length=8, default='465', choices=TYPE_CHOICES, verbose_name = "Port *")
    port_type = models.CharField(max_length=8, default='TLS/SSL',
                                 choices=_PORT_CHOICES, verbose_name = "Port Type *")
    timeout = models.IntegerField(verbose_name = "Timeout(seconds) *")

    def __str__(self):
        return u'%s' % self.email

    class Meta:
        db_table = u'send_email'