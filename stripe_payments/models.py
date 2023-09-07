from django.contrib.auth.models import User
from django.db import models
import datetime
from django.utils import timezone
from itrans.models import FileJob, Project

now = datetime.datetime.now


class StripeType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = u'stripe_type'


class StripeAccountMapping(models.Model):
    i_user = models.ForeignKey(User, on_delete=models.CASCADE)
    i_stripe = models.ForeignKey(StripeType, on_delete=models.CASCADE)
    account_ref_id = models.CharField(max_length=256)

    def __str__(self):
        return '%s-%s' % (self.i_user, self.i_stripe.name)

    class Meta:
        db_table = u'stripe_account_mapping'


class PaymentMethodMapping(models.Model):
    i_stripe_acc_mapping = models.ForeignKey(StripeAccountMapping, on_delete=models.CASCADE)
    pay_method_ref_id = models.CharField(max_length=256)
    payment_method_meta = models.JSONField()

    def __str__(self):
        return '%s' % self.i_stripe_acc_mapping

    class Meta:
        db_table = u'payment_method_mapping'


class PaymentMethodErrorLog(models.Model):
    i_stripe_acc_mapping = models.ForeignKey(StripeAccountMapping, on_delete=models.CASCADE)
    error_log = models.TextField()
    remarks = models.TextField()
    timestamp = models.DateTimeField(default=now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.i_stripe_acc_mapping

    class Meta:
        db_table = u'payment_method_error_log'


class Payments(models.Model):
    i_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)
    payment_on = models.DateTimeField(default=timezone.now)
    ref_id = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return '%s-%s' % (self.i_project.pk, self.i_project.name)

    class Meta:
        db_table = u'payments'


class ProjectPaymentErrorLog(models.Model):
    i_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    error_log = models.TextField()
    remarks = models.TextField()
    timestamp = models.DateTimeField(default=now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.pk

    class Meta:
        db_table = u'project_payment_error_log'
