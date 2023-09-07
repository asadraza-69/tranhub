import os
import shutil
import stripe
from django.conf import settings
from django.contrib.auth.models import User

from itrans.models import FileInfo, FileJob
from itrans.utils import get_time_file
from stripe_payments.models import StripeAccountMapping, PaymentMethodErrorLog, StripeType, PaymentMethodMapping, \
    ProjectPaymentErrorLog
from stripe_payments.process import create_customer, process_single_payment, \
    create_payment_method, attach_pay_method_to_stripe_customer, create_stripe_source
from user_management.models import GlobalSetting, Profile


def create_stripe_acc_mapping(user, stripe_type_obj):
    stripe_mapping, is_created = StripeAccountMapping.objects.get_or_create(i_user=user, i_stripe=stripe_type_obj)
    if is_created:
        ref_id = create_customer(user.email, stripe_type_obj)
        stripe_mapping.account_ref_id = ref_id
        stripe_mapping.save()
    return stripe_mapping


def save_pay_method_error_log(stripe_mapping, error_log='', remarks='', ip_address=''):
    response = {'status': False, 'errors': []}
    try:
        pay_method_error_log = PaymentMethodErrorLog()
        pay_method_error_log.i_stripe_acc_mapping = stripe_mapping
        pay_method_error_log.error_log = error_log
        pay_method_error_log.remarks = remarks
        pay_method_error_log.ip_address = ip_address
        pay_method_error_log.save()
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return response


def create_file_info(project_obj, file_path_list):
    response = {'status': False, 'errors': []}
    file_obj_list = []
    total_length = 0
    total_charge = 0.0
    for file_path in file_path_list:
        file_info = FileInfo()
        file_info.i_project = project_obj
        file_name = file_path
        file_name = file_name.split("/")
        file_name = file_name[len(file_name) - 1]
        file_name = file_name[15:]
        file_info.name = file_name
        new_file_path = file_path
        new_file_path = new_file_path.replace('Temp', 'itranshub/user_files')
        file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/user_files/')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, 0o777)
        shutil.copy(file_path, new_file_path)
        # os.rename(file_path, new_file_path)
        file_info.file_path = new_file_path
        file_info.save()
        filename, extension = os.path.splitext(file_name)
        data_dict = get_time_file(filename, extension, new_file_path)
        if data_dict['status']:
            length = data_dict["data"]
            file_type = data_dict["type"]
        else:
            response['errors'].append(data_dict['errors'])
            return response
        billing_charge_per_minute = GlobalSetting.objects.get(name='billing_charge_per_minute').value
        min_length = (float(length.replace("s", "")) / 60.0)
        value_with_point = min_length
        value_without_point = float(int(min_length))
        if value_without_point < value_with_point:
            min_length += 1.0
        else:
            min_length = value_without_point
        charge = float(int(min_length)) * float(billing_charge_per_minute)
        charge = str(round(charge, 2))
        # file_info.charge = charge
        file_info.length = "%s" % length
        file_info.description = file_type
        file_info.save()
        ####### File Job Work  #######
        file_job = FileJob()
        file_job.i_file = file_info
        file_job.created_by = project_obj.created_by
        file_job.charge = charge
        file_job.job_status = 'processing'
        file_job.save()
        ####### File Job Work  #######
        file_obj_list.append(file_info)
        # total_length += int(length.replace("s", ""))
        total_length += int(min_length)
        total_charge += float(charge)
    response['file_obj_list'] = file_obj_list
    response['total_length'] = total_length
    response['total_charge'] = total_charge
    response['status'] = True
    # files = glob.glob('%s/*' % os.path.join(settings.MEDIA_ROOT, 'Temp'))
    # for f in files:
    #     os.remove(f)
    return response


def save_payment(request, project_obj, save_card_details, card_token, stripe_acc_mapping_obj):
    response = {'status': False, 'errors': []}
    pay_amt = project_obj.total_charge
    print('payment_amount:', pay_amt)
    stripe_type_obj = StripeType.objects.all()[0]
    customer_stripe_ref_id = stripe_acc_mapping_obj.account_ref_id
    if save_card_details:
        pay_method_mapping_obj = PaymentMethodMapping.objects.get(i_stripe_acc_mapping=stripe_acc_mapping_obj)
        stripe_payment_method_id = pay_method_mapping_obj.pay_method_ref_id

    else:
        stripe_payment_method_id = create_stripe_source(stripe_type_obj, stripe_acc_mapping_obj, card_token)
    remarks = process_single_payment(stripe_type_obj, project_obj, customer_stripe_ref_id, stripe_payment_method_id,
                                     pay_amt)
    if remarks == 'succeeded':
        project_obj.is_paid = True
        project_obj.save()
        response['status'] = True
    else:
        response['errors'].append('Payment not successful')
    return response


def save_pay_method(request, card_token, user_email):
    response = {'status': False, 'errors': []}
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
        response['status'] = True
    return response


def save_project_payment_error_log(user_obj, error_log='', remarks='', ip_address=''):
    response = {'status': False, 'errors': []}
    try:
        project_payment_error_log = ProjectPaymentErrorLog()
        try:
            user_obj = User.objects.get(pk=user_obj.pk)
            project_payment_error_log.i_user = user_obj
        except:
            pass
        project_payment_error_log.error_log = error_log
        project_payment_error_log.remarks = remarks
        project_payment_error_log.ip_address = ip_address
        project_payment_error_log.save()
        response['status'] = True
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return response
