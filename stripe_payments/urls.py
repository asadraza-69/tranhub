from django.conf.urls import url, include
from django.urls import path
from .views import *


urlpatterns = [
    path('create_pay_method_error_log/', create_pay_method_error_log, name='create_pay_method_error_log'),
    path('save_payment_method/', save_payment_method, name='save_payment_method'),
    path('get_pub_key/', get_pub_key, name='get_pub_key'),
    path('create_project/', create_project, name='create_project'),
    path('invoice_payment_list/', invoice_payment_list, name='invoice_payment_list'),
    path('invoice_payment_listview/', invoice_payment_listview, name='invoice_payment_listview'),
    path('invoice_detail/', invoice_detail, name='invoice_detail'),
    path('edit_payment_method/', edit_payment_method, name='edit_payment_method'),
    path('delete_payment_method/', delete_payment_method, name='delete_payment_method'),
]
