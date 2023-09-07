from django.db import models


class RbacPreferenceGroup(models.Model):
    sequence = models.IntegerField()
    group = models.CharField(max_length=256)

    def __str__(self):
        return self.group

    class Meta:
        db_table = 'rbac_preference_group'


class RbacPreference(models.Model):
    group = models.ForeignKey(RbacPreferenceGroup, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    add_permission = models.CharField(max_length=256, blank=True, null=True)
    view_permission = models.CharField(max_length=256, blank=True, null=True)
    detail_permission = models.CharField(max_length=256, blank=True, null=True)
    delete_permission = models.CharField(max_length=256, blank=True, null=True)
    change_permission = models.CharField(max_length=256, blank=True, null=True)
    import_permission = models.CharField(max_length=256, blank=True, null=True)
    export_permission = models.CharField(max_length=256, blank=True, null=True)
    other_permission = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'rbac_preference'
