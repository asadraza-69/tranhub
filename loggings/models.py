from django.db import models
from django.utils import timezone


# Create your models here.
class SystemLogs(models.Model):
    action_by = models.CharField(max_length=128)
    action_by_id = models.PositiveIntegerField()
    action_date = models.DateTimeField()
    action_desc = models.CharField(default="",max_length=256)

    def __str__(self):
        return '%s-%s' % (self.action_by, self.action_date)

    class Meta:
        db_table = 'system_logs'
