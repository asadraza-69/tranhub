import json
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from permissions.models import PermissionGroups, PermissionTags
from rbac_preferences.models import RbacPreference


class PermissionGroupsBetterCreateView(CreateView):
    '''
    Group Custom better create view
    '''
    model = PermissionGroups
    template_name = 'permissions/permissiongroups_create.html'
    success_url = "/permissions/create_permissions/"
    success_message = "Permission Group was created successfully"
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        perms = []
        # print request.POST, "LISTS"

        for lst in request.POST.lists():
            if lst[0] == 'name':
                name = lst[1]
            if lst[0] == 'perms':
                for obj_p in lst[1]:
                    try:
                        perms.append(PermissionTags.objects.get(codename=obj_p).pk)
                    except Exception as e:
                        print(e)
        permission_group_obj = PermissionGroups(name=name[0])
        permission_group_obj.save()
        for record in perms:
            permission = PermissionTags.objects.get(pk=record)
            permission_group_obj.permissions.add(permission)
        return HttpResponseRedirect('/permissions/permissiongroups/')

    def get_context_data(self, **kwargs):
        '''
        Overrided function of context to give qs of permissions
        '''
        data = super(PermissionGroupsBetterCreateView, self).get_context_data(**kwargs)
        rbacs = RbacPreference.objects.all()
        rbac_list = []
        #Internal bug # 187 || LI Lite System || 19-03-2020

        rbacs = RbacPreference.objects.all()
        for rbac in rbacs:
            rbac_list.append(
                {"sequence": rbac.group.sequence, "group": rbac.group.group,
                 "title": rbac.title,
                 "add_permissions": rbac.add_permission,
                 "view_permissions": rbac.view_permission,
                 "change_permissions": rbac.change_permission,
                 "delete_permissions": rbac.delete_permission,
                 "detail_permissions": rbac.detail_permission,
                 "import_permissions": rbac.import_permission,
                 "export_permissions": rbac.export_permission,
                 "other_permissions": rbac.other_permission})
        data['rbac'] = rbac_list
        return data


class PermissionGroupsBetterUpdateView(UpdateView):
    '''
    Group Custom better Update view
    '''
    model = PermissionGroups
    permission_required = 'permissions.view_permissiongroups'
    template_name = 'permissions/permissiongroups_create.html'
    success_url = "/permissions/permissiongroups/"
    success_message = "Permission Group was updated successfully"
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        perms = []
        # print request.POST, "LISTS"
        for lst in request.POST.lists():
            if lst[0] == 'name':
                name = lst[1]
            if lst[0] == 'perms':
                for obj_p in lst[1]:
                    try:
                        perms.append(PermissionTags.objects.get(codename=obj_p).pk)
                    except Exception as e:
                        print(e)
        permission_group_obj,created = PermissionGroups.objects.get_or_create(name=name[0])
        permission_group_obj.permissions.clear()
        for record in perms:
            permission = PermissionTags.objects.get(pk=record)
            permission_group_obj.permissions.add(permission)
        return HttpResponseRedirect('/permissions/permissiongroups/')

    def get_context_data(self, **kwargs):
        '''
        Overrided function of update context
        '''
        data = super(PermissionGroupsBetterUpdateView, self).get_context_data(**kwargs)
        map_perms = data['object'].permissions.values_list('codename',
                                                           flat=True)
        rbacs = RbacPreference.objects.all()
        rbac_list = []
        for rbac in rbacs:

            rbac_list.append(
                {"sequence": rbac.group.sequence, "group": rbac.group.group,
                 "title": rbac.title,
                 "add_permissions": rbac.add_permission,
                 'add_checked': '1' if rbac.add_permission in map_perms else '0',
                 "view_permissions": rbac.view_permission,
                 'view_checked': '1' if rbac.view_permission in map_perms else '0',
                 "change_permissions": rbac.change_permission,
                 'change_checked': '1' if rbac.change_permission in map_perms else '0',
                 "delete_permissions": rbac.delete_permission,
                 'delete_checked': '1' if rbac.delete_permission in map_perms else '0',
                 "detail_permissions": rbac.detail_permission,
                 'detail_checked': '1' if rbac.detail_permission in map_perms else '0',
                 "import_permissions": rbac.import_permission,
                 'import_checked': '1' if rbac.import_permission in map_perms else '0',
                 "export_permissions": rbac.export_permission,
                 'export_checked': '1' if rbac.export_permission in map_perms else '0',
                 "other_permissions": rbac.other_permission,
                 'other_checked': '1' if rbac.other_permission in map_perms else '0'})
        permission_group_obj = PermissionGroups.objects.get(id=data['object'].pk)
        permissions_vs = permission_group_obj.permissions.values_list('codename', flat=True)
        view_perms = [perm for perm in permissions_vs if "view" in perm]

        json_list = json.dumps(view_perms)
        data['view_permissions'] = json_list
        data['rbac'] = rbac_list
        return data


class PermissionGroupsListView(ListView):
    template_name = 'permissions/permissiongroups_list.html'
    model = PermissionGroups
    ordering = ['id']
    context_object_name = 'object_list'

    # def get_queryset(self):
    #     if self.request.user.is_superuser:
    #         query_set = self.model.objects.all()
    #     else:
    #         query_set = self.model.objects.filter(i_agency=self.request.user.profile.i_agency)
    #     return query_set