import json
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from custom_auth.utils import token_authentication_func, email_code_verification_func
from loggings.utils import save_system_logs
from user_management.models import Profile
from django.contrib.auth.models import User


def get_user(email):
    try:
        user = User.objects.get(email=email.lower())
        return user.username
    except User.DoesNotExist:
        return ''


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        username = get_user(email)
        user = authenticate(username=username, password=password)
        if user and not user.is_superuser:
            if user.is_active:
                login(request, user)
                log_msg = "%s logged in the system with USERID %s" % (username, request.user.pk)
                save_system_logs(log_msg, username)
                return HttpResponseRedirect('/user_management/main_dashboard/')
            else:
                context = {"errors": "User is inactive."}
                return render(request, 'user_management/login_form.html', context)
        elif user and user.is_superuser:
            try:
                Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                Profile.objects.create(user=user)
            login(request, user)
            log_msg = "%s logged in the system with USERID %s" % (username, request.user.pk)
            save_system_logs(log_msg, username)
            return HttpResponseRedirect('/user_management/main_dashboard/')
        else:
            context = {"errors": "Please Enter A Correct Email And Password. Note That Both Fields May Be Case-Sensitive."}
            return render(request, 'user_management/login_form.html', context)
    else:
        context = {}
        return render(request, 'user_management/login_form.html', context)


def token_authentication(request):
    response_data = token_authentication_func(request)
    return HttpResponse(json.dumps(response_data))


def email_code_verification(request):
    response_data = email_code_verification_func(request)
    return HttpResponse(json.dumps(response_data))


def email_verification(request):
    return render(request, 'user_management/email_verification.html', {})


@csrf_exempt
def get_payment_info(request):
    response = {'status': False}
    try:
        if request.method == 'POST':
            email = request.POST.get('email', None)
            password = request.POST.get('password', None)
            username = get_user(email)
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    profile = Profile.objects.get(user=request.user)
                    response['payment_configured'] = profile.is_payment_configured
                    response['status'] = True
                else:
                    response['errors'] = 'User is inactive'
            else:
                response['errors'] = 'Please Enter A Correct Email And Password. Note That Both Fields May Be Case-Sensitive'
    except Exception as e:
        print('Exception:', repr(e))
        response['exception'] = repr(e)
        response['errors'] = 'Please try again'
    return JsonResponse(response)
