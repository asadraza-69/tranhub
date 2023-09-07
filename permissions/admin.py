# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
from rbac_preferences.models import *

# Register your models here.

admin.site.register(PermissionTags)
admin.site.register(PermissionGroups)
admin.site.register(RbacPreference)
admin.site.register(RbacPreferenceGroup)