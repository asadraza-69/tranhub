# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json
import pycountry
import phonenumbers
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from loggings.utils import save_system_logs
from stripe_payments.models import PaymentMethodMapping
from .country_states import COUNTRY_STATES
from .utils import *
from django.core.mail import EmailMessage, get_connection, send_mail
from .utils import account_activation_token
from django.urls import reverse
from django.shortcuts import render
import pyotp
from .models import *
from .countries import COUNTRY_CHOICES
from phonenumbers.phonenumberutil import region_code_for_number
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


@csrf_exempt
@transaction.atomic
def create_user(request):
    context = {'signup': False, 'payment_method': False}
    template_name = 'user_management/signup.html'
    try:
        if request.method == 'GET':
            template_name = 'user_management/signup.html'
            if request.user.is_authenticated:
                context['signup'] = True
                profile = Profile.objects.get(user=request.user)
                context['payment_method'] = profile.is_payment_configured
            print('context', context)
            return render(request, template_name, context)
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            company_name = request.POST.get('company')
            phone_number = request.POST.get('phone_number')
            mail_list = ["gmail", "yahoo", "hotmail", "outlook"]
            if [mail for mail in mail_list if (mail in email)]:
                context['errors'] = 'Not Business Email'
                return render(request, template_name, context)
            else:
                user = User.objects.filter(email=email)
                if user:
                    context['errors'] = 'User already exists, please sign in'
                    return render(request, template_name, context)
                else:
                    with transaction.atomic():
                        username = email.replace('@', '_')
                        user_obj = User.objects.create_user(username=username, email=email)
                        user_obj.set_password(password)
                        user_obj.first_name = first_name
                        user_obj.last_name = last_name
                        user_obj.save()
                        pn = phonenumbers.parse(phone_number)
                        country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
                        print('Post Data:', email, password, first_name, last_name, company_name, country.name, phone_number)
                        auth_info_obj = AuthInfo.objects.create(user=user_obj, secret_key=pyotp.random_base32())
                        host = request.get_host()
                        email_body = {
                            'user': user_obj,
                            'domain': host,
                            'uid': auth_info_obj.secret_key,
                            'token': account_activation_token.make_token(user_obj),
                        }
                        link = reverse('activate', kwargs={
                            'uidb64': email_body['uid'], 'token': email_body['token']})
                        email_subject = 'Activate your account'
                        activate_url = 'http://' + host + link
                        connection = get_connection(host=settings.EMAIL_HOST,
                                                    port=settings.EMAIL_PORT,
                                                    username=settings.EMAIL_HOST_USER,
                                                    password=settings.EMAIL_HOST_PASSWORD,
                                                    use_tls=settings.EMAIL_USE_TLS)
                        html_message = loader.render_to_string(
                            'user_management/account_activation.html',
                            {
                                'url': activate_url
                            }
                        )
                        mail = EmailMessage(
                            email_subject,
                            html_message,
                            settings.EMAIL_HOST_USER,
                            [user_obj.email],
                            connection=connection,
                        )
                        mail.content_subtype = "html"
                        mail.send(fail_silently=False)
                        company_obj, is_created = Company.objects.get_or_create(name=company_name)
                        profile_obj = Profile.objects.create(user=user_obj)
                        profile_obj.i_company = company_obj
                        profile_obj.country = country.name
                        profile_obj.phone_number = phone_number
                        end_trial_date = datetime.datetime.now() + datetime.timedelta(days=14)
                        profile_obj.joining_date = datetime.datetime.now()
                        profile_obj.end_trial_date = end_trial_date
                        profile_obj.is_trial_active = True
                        profile_obj.profile_completion_status = True
                        profile_obj.save()
                        return HttpResponseRedirect('/user_management/verification/')
    except Exception as e:
        number_parse_exp = 'NumberParseException'
        number_field_exp = 'LookupError'
        print('Exception: ', repr(e))
        if number_parse_exp in repr(e) or number_field_exp in repr(e):
            context['errors'] = 'Please enter correct phone number'
        else:
            context['errors'] = 'Please enter correct information'
    return render(request, template_name, context)


@csrf_exempt
@transaction.atomic
def create_profile(request):
    response = {'status': False, 'errors': []}
    context = {}
    template_name = 'user_management/signup_old.html'
    try:
        if request.method == 'GET':
            return render(request, template_name, context)
        if request.method == 'POST':
            user_id = request.POST.get('user')
            print(user_id, 'user_id')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            company_name = request.POST.get('company')
            phone_number = request.POST.get('phone_number')
            pn = phonenumbers.parse(phone_number)
            country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
            print(user_id,first_name,last_name,company_name,country.name,phone_number,'user')
            user_obj = User.objects.get(pk=user_id)
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.save()
            auth_info_obj = AuthInfo.objects.create(user=user_obj, secret_key=pyotp.random_base32())
            host = request.get_host()
            email_body = {
                'user': user_obj,
                'domain': host,
                'uid': auth_info_obj.secret_key,
                'token': account_activation_token.make_token(user_obj),
            }
            link = reverse('activate', kwargs={
                'uidb64': email_body['uid'], 'token': email_body['token']})
            email_subject = 'Activate your account'
            activate_url = 'http://' + host + link
            connection = get_connection(host=settings.EMAIL_HOST,
                                        port=settings.EMAIL_PORT,
                                        username=settings.EMAIL_HOST_USER,
                                        password=settings.EMAIL_HOST_PASSWORD,
                                        use_tls=settings.EMAIL_USE_TLS)
            html_message = loader.render_to_string(
                'user_management/account_activation.html',
                {
                    'url': activate_url
                }
            )
            mail = EmailMessage(
                email_subject,
                html_message,
                settings.EMAIL_HOST_USER,
                [user_obj.email],
                connection=connection,
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=False)
            company_obj, is_created = Company.objects.get_or_create(name=company_name)
            profile_obj = Profile.objects.get(user_id=user_id)
            profile_obj.i_company = company_obj
            profile_obj.country = country.name
            profile_obj.phone_number = phone_number
            end_trial_date = datetime.datetime.now() + datetime.timedelta(days=14)
            profile_obj.joining_date = datetime.datetime.now()
            profile_obj.end_trial_date = end_trial_date
            profile_obj.is_trial_active = True
            profile_obj.profile_completion_status = True
            profile_obj.save()
            # messages.info(request, 'Please activate your account. The activation link was sent to your email address.')
            return HttpResponseRedirect('/user_management/verification/')
    except Exception as e:
        print('Exception: ', repr(e))
        messages.error(request, 'Please enter correct information')
        return HttpResponseRedirect('/user_management/user/create/')
    return render(request, template_name, context)


def verification(request):
    template_name = 'user_management/message.html'
    return render(request, template_name, {})


@login_required
def user_list(request):
    template_name = 'user_management/user_list.html'
    return render(request, template_name)


@login_required
def user_listview(request):
    response = user_listview_func(request)
    return HttpResponse(json.dumps(response))


# @login_required
# def password_reset(request, user_id):
#     permissions = get_permission(request)
#     if permissions == True or 'can_reset_password_users' in permissions:
#         context = {}
#         status = True
#         user = None
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             raise Http404
#         except Exception as ex:
#             print 'ex = ', ex
#             messages.error(request, repr(ex))
#             status = False
#         if not status is True:
#             return HttpResponseRedirect('/auth/user/?' + request.GET.urlencode())
#         if request.method == "POST":
#             form = SetPasswordForm(user, request.POST)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Successfuly reset password')
#                 update_session_auth_hash(request, form.user)
#                 log_msg = "%s updated password of user '%s' with user ID %s" % (
#                     request.user.profile.user.username, user.username, user.id)
#                 save_system_logs(log_msg, request.user.profile.user.username)
#                 return HttpResponseRedirect('/user_management/users_list/')
#         else:
#             form = SetPasswordForm(user)
#         context['form'] = form
#         context['object'] = user
#         template = 'user_management/password_reset_form.html'
#         return render(request, template, context)
#     return HttpResponse(json.dumps({'status': 'FAILED', 'Error': 'Permission Denied.'}))


@login_required
def main_dashboard(request):
    # profile = Profile.objects.get(user=request.user)
    # if profile.is_payment_configured is False and not request.user.is_superuser:
    #     return HttpResponseRedirect('/itrans/stripe_form/')
    # else:
    return render(request, 'user_management/dashboard.html', {})


def user_logout(request):
    log_msg = "%s logged out of the system with USERID %s" % (request.user.username, request.user.id)
    save_system_logs(log_msg, request.user.username)
    logout(request)
    return HttpResponseRedirect('/accounts/login/')


@login_required
def main_dashboard_redirect(request):
    return HttpResponseRedirect('/user_management/main_dashboard/')


def activate(request, uidb64, token):
    try:
        auth_info_obj = AuthInfo.objects.get(secret_key=uidb64)
        user = auth_info_obj.user
        profile = Profile.objects.get(user=user)
        if not account_activation_token.check_token(user, token):
            messages.info(request, 'User already activated')
            return HttpResponseRedirect('/accounts/login/')
        if profile.is_email_verified:
            messages.info(request, 'User already activated')
            return HttpResponseRedirect('/accounts/login/')
        profile.is_email_verified = True
        profile.save()
        messages.info(request, 'Account activated successfully')
        return HttpResponseRedirect('/accounts/login/')
    except Exception as ex:
        print(repr(ex))
    return HttpResponseRedirect('/accounts/login/')


def get_countries(request):
    response = {'status': False, 'errors': []}
    try:
        response['status'] = True
        response['data'] = COUNTRY_CHOICES
    except Exception as e:
        response['status'] = False
        response['errors'].append(repr(e))
    return HttpResponse(json.dumps(response), content_type='application/json')


def get_country_states(request):
    response = {'status': 'FAILED', 'errors': []}
    try:
        country_id = request.GET.get('country_id', None)
        country_id = country_id.lower()
        states_list = COUNTRY_STATES[country_id]
        response['states'] = sorted(states_list)
        response['status'] = 'SUCCESS'
    except Exception as e:
        response['status'] = 'FAILED'
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def global_config(request):
    template = 'user_management/global_config.html'
    return render(request, template, {})


@login_required
@csrf_exempt
def create_global_setting(request):
    response = {'status': False, 'errors': []}
    try:
        # if request.user.is_superuser:
        global_setting_name = request.POST.get('heading')
        global_setting_value = request.POST.get('value')
        redirect_url = request.POST.get('url')
        print('Post data:', global_setting_name, global_setting_value, redirect_url)
        # redirect_url = redirect_url.split("/")[-3:]
        global_configuration_obj, is_created = GlobalSetting.objects.get_or_create(name=global_setting_name)
        global_configuration_obj.value = global_setting_value
        global_configuration_obj.save()
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def billing_charge_per_minute(request):
    context = {'value': ''}
    if request.user.is_superuser:
        try:
            global_setting_obj = GlobalSetting.objects.get(name="billing_charge_per_minute")
            context["value"] = global_setting_obj.value
        except GlobalSetting.DoesNotExist:
            context["value"] = ''
    template = 'user_management/Billing_Charges.html'
    return render(request, template, context)


@login_required
def get_global_settings(request):
    response = {'status': False, 'errors': []}
    try:
        global_setting = GlobalSetting.objects.all()
        final_dict = dict()
        for global_setting_obj in global_setting:
            m = model_to_dict(global_setting_obj)
            final_dict[m["name"]] = m["value"]
        response["data"] = final_dict
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def edit_global_settings(request):
    name = request.POST.get('name', None)
    value = request.POST.get('value', None)
    response = {'status': False, 'errors': []}
    try:
        global_setting_obj = GlobalSetting.objects.get(name=name)
        global_setting_obj.value = value
        global_setting_obj.save()
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def settings(request):
    template_name = 'user_management/settings.html'
    return render(request, template_name)


@login_required
def edit_user_profile(request):
    first_name = request.POST.get('first_name', None)
    last_name = request.POST.get('last_name', None)
    company = request.POST.get('company', None)
    phone_number = request.POST.get('phone_number', None)
    response = {'status': False, 'errors': ''}
    try:
        user = User.objects.get(pk=request.user.pk)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        pn = phonenumbers.parse(phone_number)
        country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
        profile = Profile.objects.get(user=user)
        company_obj, is_created = Company.objects.get_or_create(name=company)
        profile.i_company = company_obj
        profile.country = country.name
        profile.phone_number = phone_number
        profile.save()
        response['status'] = True
    except Exception as e:
        print('Exception: ', repr(e))
        number_parse_exp = 'NumberParseException'
        number_field_exp = 'LookupError'
        if number_parse_exp in repr(e) or number_field_exp in repr(e):
            response['errors'] = 'Please enter correct phone number'
        else:
            response['errors'] = 'Error in profile updating, please try again'
    return JsonResponse(response)


@login_required
def get_user_details(request):
    response = {}
    try:
        profile = Profile.objects.get(user=request.user)
        response['phone_number'] = str(profile.phone_number)
        response['company'] = profile.i_company.name if profile.i_company else ''
        response['first_name'] = request.user.first_name
        response['last_name'] = request.user.last_name
        response['email'] = request.user.email
        if profile.is_payment_configured:
            payment_method_obj = PaymentMethodMapping.objects.get(i_stripe_acc_mapping__i_user=request.user)
            payment_method_meta = payment_method_obj.payment_method_meta
            full_name = payment_method_meta['billing_details']['name']
            full_name = full_name.split()
            response['firstname'] = full_name[0]
            response['lastname'] = ' '.join(full_name[i] for i in range(1, len(full_name)))
            response['address'] = payment_method_meta['billing_details']['address']
            response['exp_year'] = payment_method_meta['card']['exp_year']
            response['exp_month'] = payment_method_meta['card']['exp_month']
            response['last4'] = payment_method_meta['card']['last4']
            response['brand'] = payment_method_meta['card']['brand']
    except Exception as e:
        print('Exception:', repr(e))
        response['errors'] = repr(e)
    return JsonResponse(response)


def terms_conditions(request):
    return render(request, 'user_management/terms_conditions.html')


def privacy_policy(request):
    return render(request, 'user_management/privacy_policy.html')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'user_management/profile_password_change_form.html'
    success_url = reverse_lazy('main_dashboard')

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Your password has been changed.')
        return super().form_valid(form)
