# Generated by Django 3.2 on 2021-06-18 06:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('itrans', '0006_paymentmethodmapping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripeaccountmapping',
            name='i_stripe',
        ),
        migrations.RemoveField(
            model_name='stripeaccountmapping',
            name='i_user',
        ),
        migrations.DeleteModel(
            name='PaymentMethodMapping',
        ),
        migrations.DeleteModel(
            name='StripeAccountMapping',
        ),
        migrations.DeleteModel(
            name='StripeType',
        ),
    ]
