# Generated by Django 3.2 on 2021-06-16 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('itrans', '0004_filejob_stripetype_userstripemapping'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='stripeaccountmapping',
            table='stripe_account_mapping',
        ),
    ]