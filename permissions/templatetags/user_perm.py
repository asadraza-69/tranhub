import calendar

from user_management.models import Profile
from django import template
from django.contrib.auth.models import User

from user_management.utils import get_permission
from django.conf import settings

register = template.Library()

perm_key = 'permissions_%d_%s'
perm_list_key = 'permissions_all_%d'


# @register.assignment_tag(takes_context=True)
def get_user_perm(context, perm):
    try:
        request = context['request']
        if request.user.is_superuser:
            return True
        obj = Profile.objects.get(user_id=request.user)
        result_list = []
        obj_groups = obj.permission_groups.all()
        if obj_groups:
            for groups in obj_groups:
                result_list += list(groups.permissions.values_list('codename', flat=True))
        obj_perms = obj.permission_tags.values_list('codename', flat=True)
        result_list += list(obj_perms)
        result_list = [a.lower().strip() for a in result_list]
        if perm.lower().strip() in result_list:
            return True
        return False
    except Exception as e:
        print(e)
        return False


# @register.assignment_tag(takes_context=False)
def get_version():
    return True if settings.VERSION.lower() == 'lite' else False
