from django.db import models

class PermissionTags(models.Model):
    name = models.CharField(max_length=50)
    codename = models.CharField(max_length=100)

    class Meta:
        db_table = u'permissions_tags'
        verbose_name = 'Permission Tag'
        verbose_name_plural = 'Permission Tags'

    def __str__(self):
        return self.name


class PermissionGroups(models.Model):
    name = models.CharField(max_length=80, unique=True)
    permissions = models.ManyToManyField(PermissionTags, blank=True)

    class Meta:
        db_table = u'permissions_groups'
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'

    def __str__(self):
        return self.name

