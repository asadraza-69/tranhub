from django.contrib.auth.models import User
from django.db import models
import os
import datetime
from django.conf import settings
from django.db.models import JSONField

now = datetime.datetime.now
JOB_STATUS_CHOICES = (('on hold', 'On Hold'), ('processing', 'Processing'), ('completed', 'Completed'))


def get_file_path(instance, filename):
    file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/user_files/')
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join('itranshub/user_files/', filename)


def get_transcribed_file(instance, filename):
    file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/transcribed_files/')
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join('itranshub/transcribed_files/', filename)


def get_logo_path(instance, filename):
    file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/logos/')
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join('itranshub/logos/', filename)


def get_watermarks_path(instance, filename):
    file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/watermarks/')
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join('itranshub/watermarks/', filename)


class FileInfo(models.Model):
    i_project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    length = models.CharField(max_length=128, null=True, blank=True)
    uploaded_on = models.DateTimeField(default=now)
    file_path = models.FileField(max_length=256, upload_to=get_file_path)
    transcribed_file = models.FileField(max_length=256, null=True, blank=True, upload_to=get_transcribed_file)
    transcribed_file_url = models.TextField(null=True, blank=True)
    transcribed_file_meta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return '%s-%s' % (self.pk, self.name)

    class Meta:
        db_table = u'file_info'


class FileJob(models.Model):
    i_file = models.ForeignKey(FileInfo, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    job_status = models.CharField(max_length=32, choices=JOB_STATUS_CHOICES, default='on hold')
    charge = models.DecimalField(max_digits=9, decimal_places=2)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s-%s' % (self.pk, self.i_file.name)

    class Meta:
        db_table = u'file_job'


class Vendor(models.Model):
    name = models.CharField(max_length=32)
    url = models.CharField(max_length=256, null=True, blank=True)
    shortcode = models.CharField(max_length=32, unique=True, null=True, blank=True)
    watermark = models.ImageField(max_length=256, null=True, blank=True, upload_to=get_watermarks_path)
    logo = models.ImageField(max_length=256, null=True, blank=True, upload_to=get_logo_path)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = u'vendor'


class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(default=now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    total_length = models.CharField(max_length=128, null=True, blank=True)
    total_charge = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    services = JSONField(null=True, blank=True)

    def __str__(self):
        return '%s-%s' % (self.created_by.username, self.name)

    class Meta:
        db_table = u'project'

