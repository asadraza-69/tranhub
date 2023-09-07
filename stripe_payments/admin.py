from django.contrib import admin
from .models import *

admin.site.register(StripeType)
admin.site.register(PaymentMethodMapping)
admin.site.register(PaymentMethodErrorLog)
admin.site.register(ProjectPaymentErrorLog)


class StripeAccountMappingAdmin(admin.ModelAdmin):
    list_display = ('i_user', 'i_stripe')


admin.site.register(StripeAccountMapping, StripeAccountMappingAdmin)


class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('i_project', 'paid_amount', 'remarks', 'payment_on')


admin.site.register(Payments, PaymentsAdmin)
