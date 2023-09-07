# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from mail_config.forms import EmailForm
from mail_config.models import SendEmail
from mail_config.utils import email_settings_list_view_func, update_email_settings_func
from django.http.response import HttpResponse

from user_management.utils import get_permission


def create_email_settings(request):
    permissions = get_permission(request)
    email_form = EmailForm()
    template_name = 'mail_config/create_email_settings.html'
    if permissions == True or 'can_add_email_settings' in permissions:
        if request.method == 'POST':
            email_form = EmailForm(request.POST)
            if email_form.is_valid():
                email_form.save()
                return HttpResponseRedirect('/mail_config/email_settings_list/')
            else:
                if email_form.errors:
                    print(email_form.errors)
    context = {'email_form': email_form}
    return render(request, template_name, context)


@login_required
def email_settings_list_view(request):
    response = email_settings_list_view_func(request)
    return HttpResponse(json.dumps(response))


@login_required
def email_settings_list(request):
    return render(request, 'mail_config/email_settings_list.html/', {})


@login_required
def edit_email_settings(request,setting_id):
    permissions = get_permission(request)
    if permissions == True or 'can_edit_email_settings' in permissions:
        template_name = 'mail_config/edit_email_settings.html'
        send_mail_obj = SendEmail.objects.get(pk=setting_id)
        try:
            email_form = EmailForm(instance=send_mail_obj)
        except Exception as e:
            print(repr(e))
        if request.method == 'POST':
            response = update_email_settings_func(request, setting_id)
            if response['status']:
                return HttpResponseRedirect('/mail_config/email_settings_list/')
    extra_context = {'email_form': email_form}
    return render(request, template_name, extra_context)

