# Generated by Django 3.2 on 2021-08-30 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itrans', '0011_auto_20210830_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='instant_first_draft',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='rush_my_order',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
