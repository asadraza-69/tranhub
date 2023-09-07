import os
import json
import phonenumbers
import pycountry
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import get_connection, EmailMessage
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from phonenumbers import region_code_for_number

from itrans.models import Project, FileInfo
from itrans.utils import get_file_minute
from loggings.utils import save_system_logs
from stripe_payments.models import *
from stripe_payments.process import create_payment_method, get_stripe_pub_key, create_customer, \
    attach_pay_method_to_stripe_customer
from stripe_payments.utils import create_stripe_acc_mapping, save_pay_method_error_log, save_pay_method, save_payment, \
    create_file_info, save_project_payment_error_log
from user_management.models import Profile, Company, GlobalSetting


@csrf_exempt
def save_payment_method(request):
    response = {'status': False, 'errors': []}
    try:
        try:
            ip_address = request.META['HTTP_X_FORWARDED_FOR']
        except:
            ip_address = ''
        card_token = request.POST.get('token')
        user_email = request.POST.get('UserEmail')
        print(card_token, user_email)
        stripe_mapping = StripeAccountMapping.objects.get(i_user__email=user_email)
        pay_method_object = create_payment_method(stripe_mapping.i_stripe, card_token)
        if pay_method_object:
            pay_method_mapping_obj = PaymentMethodMapping.objects.create(i_stripe_acc_mapping=stripe_mapping,
                                                payment_method_meta=pay_method_object,
                                                pay_method_ref_id=pay_method_object['id'])
            customer_stripe_ref_id = stripe_mapping.account_ref_id
            stripe_payment_method_id = pay_method_mapping_obj.pay_method_ref_id
            attach_pay_method_to_stripe_customer(stripe_mapping.i_stripe, customer_stripe_ref_id, stripe_payment_method_id)
            profile = Profile.objects.get(user__email=user_email)
            profile.is_payment_configured = True
            profile.save()
            # messages.info(request, 'Your card details saved successfully')
            response['status'] = True
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        print('Status is: %s' % e.http_status)
        print('Code is: %s' % e.code)
        # param is '' in this case
        print('Param is: %s' % e.param)
        print('Message is: %s' % e.user_message)
        error_log = repr(e)
        remarks = e.user_message
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (e.user_message, repr(e))
        response['errors'].append(errors)
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        error_log = repr(e)
        remarks = "Too many requests made to the API too quickly"
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        error_log = repr(e)
        remarks = "Invalid parameters were supplied to Stripe's API"
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        error_log = repr(e)
        remarks = "Authentication with Stripe's API failed(maybe you changed API keys recently)"
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        error_log = repr(e)
        remarks = "Network communication with Stripe failed"
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        error_log = repr(e)
        remarks = "Payment Error"
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except Exception as e:
        print('Exception Occurred: ', repr(e))
        error_log = repr(e)
        remarks = repr(e)
        save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        response['errors'].append(repr(e))
    return JsonResponse(response)


def get_pub_key(request):
    response = {'status': False, 'errors': []}
    try:
        stripe_type_obj = StripeType.objects.all()[0]
        print(stripe_type_obj, 'stripe_type_obj')
        stripe_pub_key = get_stripe_pub_key(stripe_type_obj)
        response['pub_key'] = stripe_pub_key
        response['status'] = True
    except Exception as e:
        print('Exception:', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@csrf_exempt
def create_pay_method_error_log(request):
    response = {'status': False, 'errors': []}
    try:
        user_email = request.POST.get('UserEmail')
        stripe_mapping = StripeAccountMapping.objects.get(i_user__email=user_email)
        error_log = request.POST.get('error_log')
        remarks = request.POST.get('remarks')
        try:
            ip_address = request.META['HTTP_X_FORWARDED_FOR']
        except:
            ip_address = ''
        res = save_pay_method_error_log(stripe_mapping, error_log, remarks, ip_address)
        if res['status']:
            response['status'] = True
        else:
            response['errors'].append(res['errors'])
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@csrf_exempt
@transaction.atomic
def create_project(request):
    response = {'status': False, 'errors': ''}
    try:
        if request.method == 'POST':
            try:
                ip_address = request.META['HTTP_X_FORWARDED_FOR']
            except:
                ip_address = ''
            user_obj = None
            card_token = request.POST.get('token')
            project_name = request.POST.get('project_name')
            project_description = request.POST.get('Extra_Comment')
            file_paths_list = request.POST.get('file_paths')
            file_paths_list = json.loads(file_paths_list)
            save_card_details = request.POST.get('Save_Card_Details', False)
            email = request.POST.get('email')
            email = email.lower() if email else email
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            company_name = request.POST.get('company')
            phone_number = request.POST.get('phone_number')
            services_json = request.POST.get('services')
            user_uuid = request.POST.get('uuid', None)
            if services_json:
                services_json = json.loads(services_json)
            total_charges = request.POST.get('TotalCharges')
            with transaction.atomic():
                if request.user.is_authenticated:
                    user_obj = request.user
                else:
                    user = User.objects.filter(email=email)
                    if user:
                        response['errors'] = 'This email already exist please sign in'
                        return JsonResponse(response)
                    else:
                        username = email.replace('@', '_')
                        user_obj = User.objects.create_user(username=username, email=email)
                        user_obj.set_password(password)
                        user_obj.first_name = first_name
                        user_obj.last_name = last_name
                        user_obj.save()
                        pn = phonenumbers.parse(phone_number)
                        country = pycountry.countries.get(alpha_2=region_code_for_number(pn))
                        company_obj, is_created = Company.objects.get_or_create(name=company_name)
                        profile_obj = Profile.objects.create(user=user_obj)
                        profile_obj.i_company = company_obj
                        profile_obj.country = country.name
                        profile_obj.phone_number = phone_number
                        profile_obj.save()
                        try:
                            email_subject = 'Welcome to iTrans'
                            connection = get_connection(host=settings.EMAIL_HOST,
                                                        port=settings.EMAIL_PORT,
                                                        username=settings.EMAIL_HOST_USER,
                                                        password=settings.EMAIL_HOST_PASSWORD,
                                                        use_tls=settings.EMAIL_USE_TLS,
                                                        timeout=settings.EMAIL_TIMEOUT)
                            html_message = loader.render_to_string('user_management/welcome_page.html', {})
                            mail = EmailMessage(email_subject, html_message, settings.EMAIL_HOST_USER,
                                                [user_obj.email], connection=connection, )
                            mail.content_subtype = "html"
                            mail.send(fail_silently=True)
                        except Exception as e:
                            print('Exception: ', repr(e))
                project_obj = Project.objects.create(name=project_name, description=project_description,
                                                     created_by=user_obj, services=services_json)
                file_info_resp = create_file_info(project_obj, file_paths_list)
                total_length = file_info_resp['total_length']
                project_obj.total_length = total_length
                project_obj.total_charge = float(total_charges)
                project_obj.save()
                stripe_type_obj = StripeType.objects.all()[0]
                user_stripe_mapping_obj = create_stripe_acc_mapping(user_obj, stripe_type_obj)
                profile_obj = Profile.objects.get(user=user_obj)
                if save_card_details:
                    if not profile_obj.is_payment_configured:
                        save_pay_method_resp = save_pay_method(request, card_token, user_obj.email)
                    save_payment_resp = save_payment(request, project_obj, save_card_details, card_token, user_stripe_mapping_obj)
                else:
                    if request.user.is_authenticated:
                        if profile_obj.is_payment_configured:
                            save_card_details = True
                    save_payment_resp = save_payment(request, project_obj, save_card_details, card_token, user_stripe_mapping_obj)
                print('save_payment_resp:', save_payment_resp)
                if not request.user.is_authenticated:
                    user = authenticate(username=user_obj.username, password=password)
                    login(request, user)
                log_msg = "%s-%s created %s-%s project and pay $%s" % (user_obj.pk, user_obj.username, project_obj.pk,
                                                                       project_obj.name, project_obj.total_charge)
                save_system_logs(log_msg, user_obj.username)
                response['status'] = True
            try:
                for f in file_paths_list:
                    os.remove(f)
            except Exception as e:
                print('Exception: ', repr(e))
    except stripe.error.CardError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = e.user_message
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.RateLimitError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Too many requests made to the API too quickly"
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.InvalidRequestError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Invalid parameters were supplied to Stripe's API"
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.AuthenticationError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Authentication with Stripe's API failed(maybe you changed API keys recently)"
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.APIConnectionError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Network communication with Stripe failed"
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.StripeError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Payment Error"
        save_project_payment_error_log(user_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except Exception as e:
        print('Exception: ', repr(e))
        response['exception'] = repr(e)
        error_log = repr(e)
        number_parse_exp = 'NumberParseException'
        number_field_exp = 'LookupError'
        if number_parse_exp in repr(e) or number_field_exp in repr(e):
            response['errors'] = 'Please enter correct phone number'
        else:
            response['errors'] = 'Error in project creation, please try again'
        save_project_payment_error_log(user_obj, error_log, response['errors'], ip_address)
    return JsonResponse(response)


@login_required
def invoice_payment_list(request):
    log_msg = "%s Visited Invoice Payment List" % (
        request.user.username)
    save_system_logs(log_msg, request.user.username)
    template = 'stripe_payments/invoice_payment_list.html'
    return render(request, template, {})


@login_required
def invoice_payment_listview(request):
    project_id = request.GET.get('project_id')
    response = {'status': False, 'errors': []}
    try:
        if project_id:
            invoice_payments_list = Payments.objects.filter(i_project_id=project_id).order_by('-pk')
        elif request.user.is_superuser:
            invoice_payments_list = Payments.objects.all().order_by('-pk')
        else:
            invoice_payments_list = Payments.objects.filter(i_project__created_by=request.user).order_by('-pk')
        rows = []
        response['headers'] = ['Project Name', 'Paid Amount', 'Remarks',
                               'Payment On', 'Ref. No']
        # permissions = get_permission(request)
        # if permissions == True or 'can_view_invoice_payment_list' in permissions:
        for invoice_payments in invoice_payments_list:
            temp = list()
            temp.append([invoice_payments.i_project.name, ''])
            temp.append(['$ %s' % invoice_payments.paid_amount, ''])
            temp.append([invoice_payments.remarks, ""])
            temp.append([invoice_payments.payment_on.strftime(
                '%Y-%m-%d %H:%M:%S') if invoice_payments.payment_on else '-', ''])
            temp.append([invoice_payments.ref_id, ""])
            rows.append(temp)
        response['status'] = True
        response['data'] = rows
        response['page_title'] = "Invoice Payment"
        response['page_list_title'] = ""
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def invoice_detail(request):
    response = {'status': False, 'errors': []}
    try:
        data = {'file': [], 'services': []}
        project_id = request.GET.get('project_id')
        payment_obj = Payments.objects.get(i_project_id=project_id)
        file_info_obj = FileInfo.objects.filter(i_project_id=project_id)
        files_count = float(len(file_info_obj))
        project_obj = payment_obj.i_project
        services_json = project_obj.services
        if services_json:
            data['services'].append(services_json)
        for file_info in file_info_obj:
            file_job = FileJob.objects.get(i_file=file_info)
            file_dict = dict()
            file_dict['amount'] = file_job.charge
            file_dict['name'] = file_info.name
            file_dict['length'] = '%s min(%s)' % (get_file_minute(file_info.length), file_info.length)
            data['file'].append(file_dict)
        data['total'] = payment_obj.paid_amount
        data['files_count'] = files_count
        response['data'] = data
        response['status'] = True
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def edit_payment_method(request):
    response = {'status': False}
    try:
        ip_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        ip_address = ''
    try:
        if request.method == 'POST':
            with transaction.atomic():
                card_token = request.POST.get('token')
                stripe_acc_mapping = StripeAccountMapping.objects.get(i_user=request.user)
                pay_method_object = create_payment_method(stripe_acc_mapping.i_stripe, card_token)
                try:
                    payment_method_obj = PaymentMethodMapping.objects.get(i_stripe_acc_mapping=stripe_acc_mapping)
                    payment_method_obj.payment_method_meta = pay_method_object
                    payment_method_obj.pay_method_ref_id = pay_method_object['id']
                    payment_method_obj.save()
                except:
                    payment_method_obj = PaymentMethodMapping.objects.create(i_stripe_acc_mapping=stripe_acc_mapping,
                                                                             payment_method_meta=pay_method_object,
                                                                             pay_method_ref_id=pay_method_object['id'])
                    profile_obj = Profile.objects.get(user=request.user)
                    profile_obj.is_payment_configured = True
                    profile_obj.save()
                customer_stripe_ref_id = stripe_acc_mapping.account_ref_id
                stripe_payment_method_id = payment_method_obj.pay_method_ref_id
                attach_pay_method_to_stripe_customer(stripe_acc_mapping.i_stripe, customer_stripe_ref_id,
                                                     stripe_payment_method_id)
                response['status'] = True
    except stripe.error.CardError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = e.user_message
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.RateLimitError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Too many requests made to the API too quickly"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.InvalidRequestError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Invalid parameters were supplied to Stripe's API"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.AuthenticationError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Authentication with Stripe's API failed(maybe you changed API keys recently)"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.APIConnectionError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Network communication with Stripe failed"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except stripe.error.StripeError as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "Payment Error"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, error_log)
        response['errors'] = errors
    except Exception as e:
        print('Exception: ', repr(e))
        error_log = repr(e)
        remarks = "General Exception"
        save_pay_method_error_log(stripe_acc_mapping, error_log, remarks, ip_address)
        response['errors'] = 'Error in payment method process, please try again'
    return JsonResponse(response)


@login_required
def delete_payment_method(request):
    response = {'status': False}
    try:
        with transaction.atomic():
            PaymentMethodMapping.objects.get(i_stripe_acc_mapping__i_user=request.user).delete()
            profile_obj = Profile.objects.get(user=request.user)
            profile_obj.is_payment_configured = False
            profile_obj.save()
            response['status'] = True
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'] = repr(e)
    return JsonResponse(response)
