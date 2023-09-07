from django.urls import path
from .views import *


urlpatterns = [
    path('get_payment_info/', get_payment_info, name='get_payment_info'),
]
