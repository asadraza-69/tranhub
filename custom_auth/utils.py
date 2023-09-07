import binascii
import datetime
import os

import pyotp
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from custom_auth.models import AuthInfo
from user_management.models import ClientVerification, SessionCredentials
from user_management.utils import check_client_access_info, set_client_info, create_client_verification, \
    send_verification_email


def token_authentication_func(request):
    user_given_token = request.POST['otp']
    username = request.session["username"]
    password = request.session["password"]
    src = request.session["src"]
    response_data = dict()
    user = authenticate(username=username, password=password)
    if user_given_token:
        user_given_token = str(user_given_token)
        is_valid = pyotp.TOTP(AuthInfo.objects.get(user=user).secret_key).verify(user_given_token)
        profile_obj = user.profile
        if is_valid:
            if not user.profile.qr_verified:
                profile_obj.qr_verified = True
                profile_obj.save()
            suspicious = check_client_access_info(request)
            if suspicious:
                user = User.objects.get(username=username)
                create_client_verification(request)
                response = send_verification_email(request, user)
                return response
            login(request, user)
            del request.session['username']
            del request.session['password']
            del request.session['src']
            response_data['status'] = 'SUCCESS'
            response_data['url'] = '/user_management/main_dashboard/'
            # if not request.user.is_anonymous:
            #     session_obj = Session.objects.get(session_key=request.session.session_key)
            #     session_credential = SessionCredentials()
            #     session_credential.token = binascii.hexlify(os.urandom(20)).decode()
            #     session_credential.i_session = session_obj
            #     session_credential.save()
        else:
            # logout(request)
            response_data['status'] = 'FAILED'
    print(response_data, 'ss')
    return response_data


def email_code_verification_func(request):
    email_code = request.POST.get('email_code', None)
    username = request.POST['username']
    password = request.POST['password']
    response_data = dict()
    try:
        user_obj = authenticate(username=username, password=password)
        data_dict = {'i_profile': user_obj.profile, 'verification_code': int(email_code),
                     'expiry_date__gte': datetime.datetime.now()}
        client_obj = ClientVerification.objects.get(**data_dict)
        chk_var = client_obj.verification_code
    except Exception as e:
        response_data['status'] = 'FAILED'
        response_data['error'] = 'Verification code was not validated.'
        client_obj = None
        chk_var = None
    if (str(chk_var) == str(email_code)):
        try:
            user = authenticate(username=username, password=password)
            login(request, user)
            del request.session['username']
            del request.session['password']
            del request.session['src']
            # if not request.user.is_anonymous:
            #     session_obj = Session.objects.get(session_key=request.session.session_key)
            #     session_credential = SessionCredentials()
            #     session_credential.token = binascii.hexlify(os.urandom(20)).decode()
            #     session_credential.i_session = session_obj
            #     session_credential.save()
        except Exception as e:
            response_data['status'] = 'FAILED'
            response_data['error'] = repr(e)
        if client_obj:
            client_obj.delete()
        set_client_info(request)
        response_data['status'] = 'SUCCESS'
        response_data['url'] = '/user_management/main_dashboard/'
    else:
        response_data['status'] = 'FAILED'
    return response_data
