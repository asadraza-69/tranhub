# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-09-08 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'db_table': 'permissions_groups',
                'verbose_name': 'Permission Group',
                'verbose_name_plural': 'Permission Groups',
            },
        ),
        migrations.CreateModel(
            name='PermissionTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'permissions_tags',
                'verbose_name': 'Permission Tag',
                'verbose_name_plural': 'Permission Tags',
            },
        ),
        migrations.AddField(
            model_name='permissiongroups',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='permissions.PermissionTags'),
        ),
    ]
