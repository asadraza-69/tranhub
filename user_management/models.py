# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.db import models
from permissions.models import PermissionTags, PermissionGroups
now = datetime.datetime.now


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='i_user')
    qr_verified = models.BooleanField(default=False)
    permission_tags = models.ManyToManyField(PermissionTags, blank=True, related_name='i_permission_tags')
    permission_groups = models.ManyToManyField(PermissionGroups, blank=True, related_name='i_permission_groups')
    i_company = models.ForeignKey("Company", on_delete=models.CASCADE, null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    joining_date = models.DateTimeField(null=True, blank=True)
    end_trial_date = models.DateTimeField(null=True, blank=True)
    is_trial_active = models.BooleanField(default=False)
    is_payment_configured = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    profile_completion_status = models.BooleanField(default=False)

    def __str__(self):
        return '%s | %s %s' % (self.user.username, self.user.first_name, self.user.last_name)

    class Meta:
        db_table = u'profile'


class ClientDetails(models.Model):
    browser_os = models.CharField(max_length=256)
    hardware = models.CharField(max_length=256)
    country = models.CharField(max_length=256,default="default")
    user_ip = models.CharField(max_length=256,default="user_ip")
    system_hardware = models.CharField(max_length=256,default="default")
    i_profile = models.ForeignKey("Profile", on_delete=models.CASCADE)

    def __str__(self):
        return '%s | %s ' % (self.i_profile,self.user_ip)

    class Meta:
        db_table = u'client_details'


class ClientVerification(models.Model):
    verification_code = models.PositiveIntegerField()
    email_sent = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(editable=False)
    i_profile = models.ForeignKey("Profile", on_delete=models.CASCADE)

    def __str__(self):
        return '%s | %s ' % (self.verification_code,self.i_profile)

    class Meta:
        db_table = u'client_verification'


class SessionCredentials(models.Model):
    i_session = models.ForeignKey("sessions.Session", on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

    class Meta:
        db_table = u'session_credentials'


class GlobalSetting(models.Model):
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=32)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = u'global_setting'


class Company(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = u'company'

