import datetime
import random
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
import httpagentparser
# import pyotp
import requests
from django.db import IntegrityError
from django.template import loader
from custom_auth.models import AuthInfo
from loggings.utils import save_system_logs
from mail_config.models import SendEmail
from mail_config.utils import send_email_func
from .forms import UserForm, ProfileForm, UserUpdateForm, CompanyForm
from .models import *


def get_permission(request):
    try:
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
        return result_list
    except Exception as e:
        print(e)
        return [""]


def user_listview_func(request):
    response = {}
    rows = []
    response['headers'] = ['Username', 'Name', 'Email Address', 'Company Name', 'Phone Number', 'User Status', 'Joining Date', 'Last Login', 'Action']
    users_qs = Profile.objects.all().exclude(user__is_superuser=True).order_by('pk')
    log_msg = "%s visited User Management Page" % request.user.username
    save_system_logs(log_msg, request.user.username)
    permissions = get_permission(request)
    if permissions == True or 'can_view_user' in permissions:
        for users_obj in users_qs:
            actions = list()
            btn_list = list()
            if permissions == True or 'can_edit_user' in permissions:
                edit_btn = ["/user_management/user/update/" + str(users_obj.user.pk) + "", "Edit", ""]
                btn_list.append(edit_btn)
            if permissions == True or 'can_reset_password_users' in permissions:
                up_pass_btn = ["/accounts/password/reset/" + str(users_obj.user.pk) + "", "Update Password", ""]
                btn_list.append(up_pass_btn)
            if btn_list:
                actions.append(btn_list)
            else:
                actions.append([])
            actions.append("action")
            temp = list()
            temp.append([users_obj.user.username, str(users_obj.user.pk)])
            temp.append([users_obj.user.first_name + " " + users_obj.user.last_name, ""])
            temp.append([users_obj.user.email, ""])
            temp.append([users_obj.i_company.name, ""])
            temp.append([users_obj.phone_number, ""])
            temp.append(['True' if users_obj.user.is_active else 'False', ""])
            temp.append([users_obj.joining_date.strftime('%Y-%m-%d %H:%M:%S') if users_obj.joining_date else "-", ""])
            temp.append(
                [users_obj.user.last_login.strftime('%Y-%m-%d %H:%M:%S') if users_obj.user.last_login else "-", ""])
            temp.append(actions)
            rows.append(temp)
    response['data'] = rows
    response['page_title'] = "User"
    response['page_list_title'] = "User List"
    response['model_name'] = "User"
    response['breadcrums'] = ""
    return response


def create_user_func(request):
    response = {}
    user_form = UserForm(request.POST)
    profile_form = ProfileForm(request.POST)
    company_form = CompanyForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid() and company_form.is_valid():
        try:
            user = user_form.save(commit=False)
            user.is_active = True
            user.username = user_form.cleaned_data['email']
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            import pyotp
            AuthInfo.objects.create(user=user, secret_key=pyotp.random_base32())
            # company_obj = Company.objects.create(name=company_name)
            company = company_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.i_company = company
            end_trial_date = datetime.datetime.now() + datetime.timedelta(days=14)
            profile.end_trial_date = end_trial_date
            profile.is_trial_active = True
            profile = profile_form.save()
            profile.save()
            log_msg = "%s created user with username '%s' with user ID %s" % (
                request.user.profile.user.username, profile.user.username, user.id)
            save_system_logs(log_msg, request.user.profile.user.username)
            response['status'] = True
        except IntegrityError as ex:
            if 'unique constraint' in ex.message:
                response['error'] = 'User already registered'
                response['status'] = False
        except Exception as ex:
            print("An exception occured", ex)
            response['status'] = False
    else:
        if profile_form.errors:
            response['error'] = profile_form.errors
        elif user_form.errors:
            response['error'] = user_form.errors
            print(user_form.errors)
        response['status'] = False
        print("Form not valid")
    return response


def update_user_func(request, user_id):
    user = User.objects.get(pk=user_id)
    profile = Profile.objects.get(pk=user)
    response = {}
    user_form = UserUpdateForm(request.POST, instance=user)
    profile_form = ProfileForm(request.POST, instance=profile)
    if user_form.is_valid() and profile_form.is_valid():
        try:
            user = user_form.save()
            profile = profile_form.save()
            log_msg = "%s updated profile of '%s' with user ID %s" % (
                request.user.username, user.username, user.id)
            save_system_logs(log_msg, request.user.username)
            response['status'] = True
        except Exception as ex:
            print("An exception occured", ex)
            response['status'] = False
    else:
        if profile_form.errors:
            response['error'] = profile_form.errors
        elif user_form.errors:
            response['error'] = user_form.errors
        response['status'] = False

    return response


def create_client_verification(request):
    response = {'status': 'FAILED', 'errors': []}
    try:
        username = request.session.get('username')
        profile_id = Profile.objects.get(user__username=username).pk
        client_verification_qs = ClientVerification.objects.filter(i_profile_id=profile_id,
                                                                   expiry_date__lte=datetime.datetime.now())
        if client_verification_qs:
            client_verification_qs.delete()
        vc = int(''.join(str(random.randint(1, 9)) for _ in range(0, 6)))
        hours_added = datetime.timedelta(hours=1)
        expiry_date = datetime.datetime.now() + hours_added
        defaults_dict = {'verification_code': vc, 'expiry_date': expiry_date}
        obj, is_created = ClientVerification.objects.get_or_create(i_profile_id=profile_id,
                                                                   expiry_date__gte=datetime.datetime.now(),
                                                                   defaults=defaults_dict)

        obj.save()
        response['status'] = 'SUCCESS'
    except Exception as e:
        response['errors'].append(repr(e))
        response['status'] = 'FAILED'
    return response


def set_client_info(request, profile=None):
    response = {'status': 'FAILED', 'errors': []}
    try:
        client_response = get_client_detail_dict(request)
        data_dict = client_response['data']
        profile_id = profile if profile else request.user.profile.pk
        attrs = {'browser_os': data_dict['browser_os'], 'hardware': data_dict['hardware'], 'country': data_dict['country'],
                 'user_ip': data_dict['user_ip'], 'system_hardware': data_dict['system_hardware'],
                 'i_profile_id': profile_id}
        obj = ClientDetails(**attrs)
        obj.save()
        response['status'] = 'SUCCESS'
    except Exception as e:
        response['errors'].append(repr(e))
        response['status'] = 'FAILED'
    return response


def check_client_access_info(request):
    response = {'status': 'FAILED', 'errors': []}
    try:
        username = request.session.get('username')
        user_id = Profile.objects.get(user__username=username).pk
        client_response = get_client_detail_dict(request)
        data_dict = client_response['data']
        client_detail_obj = None
        client_detail_qs = ClientDetails.objects.filter(i_profile_id=user_id).order_by('-pk')
        if client_detail_qs:
            client_detail_obj = client_detail_qs[0]
        else:
            set_client_info(request, user_id)
        suspicious = False
        if client_detail_obj and (data_dict['browser_os'] != client_detail_obj.browser_os):
            suspicious = True
        elif client_detail_obj and (data_dict['hardware'] != client_detail_obj.hardware):
            suspicious = True
        elif client_detail_obj and (data_dict['country'] != client_detail_obj.country):
            suspicious = True
        elif client_detail_obj and (data_dict['system_hardware'] != client_detail_obj.system_hardware):
            suspicious = True
        elif client_detail_obj and (data_dict['user_ip'] != client_detail_obj.user_ip):
            suspicious = True
        return suspicious
    except Exception as e:
        response['errors'].append(repr(e))
        response['status'] = 'FAILED'
    return response


def send_verification_email(request, user):
    response_data = {'status': 'FAILED', 'errors': []}
    try:
        data_dict = get_client_detail_dict(request)
        data_dict = data_dict['data']
        client_v_obj = ClientVerification.objects.get(i_profile_id=user.profile.pk)
        verification_code = client_v_obj.verification_code
        v_code = str(verification_code)
        system_name = data_dict['hardware']
        browser_name = data_dict['browser_os']
        first_name = user.first_name
        user_name = user.username
        email = user.email
        user_ip = data_dict['user_ip']
        hardware_name = data_dict['system_hardware']
        date_time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        user_country = data_dict['country']
        send_mail_obj = SendEmail.objects.get(category='verification_code')
        subject = 'System Verification Code'
        email_list = []
        email_list.append(user.email)
        html_message = loader.render_to_string(
            'user_management/email_template.html',
            {
                'system_name': system_name,
                'browser_name': browser_name,
                'first_name': first_name,
                'username': user_name,
                'hardware_name': hardware_name,
                'date_time': date_time,
                'country': user_country,
                'user_ip': user_ip,
                'verfication_code': str(verification_code),
                'email': email,
            }
        )
        send_email_resp = send_email_func(send_email_obj=send_mail_obj, subject=subject, users_list=email_list,
                                          body_text=v_code, html_message=html_message)
        if send_email_resp == 1:
            response_data['status'] = 'SUCCESS'
            response_data['email_sent'] = True
            client_v_obj.email_sent = True
            client_v_obj.save()
        else:
            response_data['status'] = 'FAILED'
            response_data['email_sent'] = False
    except Exception as e:
        response_data['errors'].append(repr(e))
        response_data['status'] = 'FAILED'
    return response_data


def get_client_detail_dict(request):
    response = {}
    try:
        http_user_agent = request.META["HTTP_USER_AGENT"]
        browser_os = httpagentparser.simple_detect(http_user_agent)
        browser = browser_os[1]
        hardware = browser_os[0]
        user_ip = request.META.get('REMOTE_ADDR')
        system_hardware = request.META.get('HTTP_USER_AGENT')
        system_hardware = system_hardware[system_hardware.find("(") + 1: system_hardware.find(")")]
        if user_ip == '127.0.0.1':
            url = 'http://ip-api.com/json/'
        else:
            url = 'http://ip-api.com/json/%s' % (user_ip)
        response = requests.get(url).json()
        user_country = '%s-%s-%s' % (response.get('city'), response.get('country'), response.get('regionName'))
        response['status'] = 'SUCCESS'

    except Exception as e:
        print(repr(e))
        browser = ""
        hardware = ""
        system_hardware = ""
        user_ip = ""
        user_country = ""
        response['error'] = repr(e)
        response['status'] = 'FAILED'
    data_dict = {'browser_os': browser, 'hardware': hardware, 'country': user_country, 'user_ip': user_ip,
                 'system_hardware': system_hardware}
    response['data'] = data_dict
    return response


def check_validation():
    allow_access = ''
    # global_setting_obj = GlobalSetting.objects.all()
    # if global_setting_obj:
    #     allow_access = global_setting_obj[0].allow_access
    # else:
    #     global_setting_obj = GlobalSetting.objects.create(allow_access=False)
    #     allow_access = global_setting_obj.allow_access
    return allow_access


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


account_activation_token = AppTokenGenerator()