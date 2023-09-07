# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import *

# admin.site.register(ClientDetails)
# admin.site.register(ClientVerification)
admin.site.register(Company)
# admin.site.register(SessionCredentials)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'i_company', 'country', 'phone_number', 'is_payment_configured')


admin.site.register(Profile, ProfileAdmin)


class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


admin.site.register(GlobalSetting, GlobalSettingAdmin)
