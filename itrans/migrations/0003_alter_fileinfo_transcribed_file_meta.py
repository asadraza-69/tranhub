# Generated by Django 3.2 on 2021-06-11 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itrans', '0002_auto_20210611_0717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileinfo',
            name='transcribed_file_meta',
            field=models.JSONField(blank=True, null=True),
        ),
    ]