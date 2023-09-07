import re
import stripe
import yaml
from django.conf import settings
from itrans.models import Vendor
from stripe_payments.models import Payments


def get_stripe_config():
    config_path = settings.YAML_FILE_PATH
    with open(config_path) as file:
        s_config_dict = yaml.load(file, Loader=yaml.FullLoader)
    return s_config_dict


def get_stripe_pub_key(stripe_type_obj):
    s_config_dict = get_stripe_config()
    stripe_name = stripe_type_obj.name
    pub_key_name = stripe_name + '_PUB_KEY'
    print('pub_key_name is :', pub_key_name)
    try:
        PUB_KEY = s_config_dict[pub_key_name]
        print('TRY PUB KEY is : ', PUB_KEY)
    except:
        PUB_KEY = s_config_dict['PUB_KEY']
        print('EXCEPT PUB KEY is : ', PUB_KEY)
    return PUB_KEY


def create_customer(cust_email, stripe_type_obj):
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    stripe_customer = stripe.Customer.create(
                    email=cust_email)
    profile_ref_id = stripe_customer['id']
    return profile_ref_id


def create_payment_method(stripe_type_obj, card_token):
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    pay_method_object = stripe.PaymentMethod.create(
                                type="card",
                                card=dict(token=card_token),
                            )
    return pay_method_object


def retrieve_payment_method(stripe_type_obj):
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    pay_method_retrieve = stripe.PaymentMethod.retrieve(
        "pm_1J3EVeHRXGiggfuwoB2TOuoa", # payment_method_object['id']
    )
    return pay_method_retrieve


def attach_pay_method_to_stripe_customer(stripe_type_obj, customer_stripe_ref_id, stripe_payment_method_id):
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    stripe.PaymentMethod.attach(
      stripe_payment_method_id,
      customer=customer_stripe_ref_id,
    )


def create_stripe_source(stripe_type_obj, user_stripe_mapping_obj, card_token, currency_type = 'usd'):
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    source_obj = stripe.Source.create(type="card",
                                      currency=currency_type,
                                      owner={"email": user_stripe_mapping_obj.i_user.email},

                                      token=card_token,
                                      )
    stripe_customer = stripe.Customer.modify(user_stripe_mapping_obj.account_ref_id,
                                             source=source_obj.get('id'),
                                             )
    stripe_payment_method_id = stripe_customer['default_source']
    return stripe_payment_method_id


def process_single_payment(stripe_type_obj, project_obj, customer_stripe_ref_id, stripe_payment_method_id, pay_amt, currency_type = 'usd'):
    confirm = True
    stripe.api_key = get_stripe_secret_key(stripe_type_obj)
    vendor_obj = Vendor.objects.all()[0]
    vendor_name = vendor_obj.name
    clean_vendor_name = re.sub('[^A-Za-z0-9 ]+', '', vendor_name)
    pay_intent = stripe.PaymentIntent.create(
                            customer=customer_stripe_ref_id,\
                            payment_method=stripe_payment_method_id,\
                            amount=int((pay_amt)*100),\
                            currency=currency_type,\
                            confirm=confirm,\
                            description=clean_vendor_name + ' - ' + str(project_obj.id),\
                            metadata={'bits_project_id':project_obj.id,\
                                      'bits_description':clean_vendor_name + ' - ' + str(project_obj.id),}, \
                            statement_descriptor=clean_vendor_name.encode('utf-8')[:20], \
                            )
    remarks = pay_intent.get('status')
    print('remarks:', remarks)
    if remarks == 'succeeded':
        transaction_id = pay_intent['charges']['data'][0]['id']
        payment_obj = Payments()
        payment_obj.i_project = project_obj
        payment_obj.paid_amount = pay_intent["amount_received"]/100.0
        payment_obj.remarks = remarks
        payment_obj.ref_id = transaction_id
        payment_obj.save()
    return remarks


def get_stripe_secret_key(stripe_type_obj):
    s_config_dict = get_stripe_config()
    stripe_name = stripe_type_obj.name
    sec_key_name = stripe_name + '_SEC_KEY'
    try:
        SEC_KEY = s_config_dict[sec_key_name]
    except:
        SEC_KEY = s_config_dict['SEC_KEY']
    return SEC_KEY
