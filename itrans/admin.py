from django.contrib import admin
from itrans.models import *

admin.site.register(Vendor)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_length', 'total_charge', 'is_paid', 'created_on', 'created_by')


admin.site.register(Project, ProjectAdmin)


class FileJobAdmin(admin.ModelAdmin):
    list_display = ('i_file', 'charge', 'job_status', 'remarks', 'created_on', 'created_by')


admin.site.register(FileJob, FileJobAdmin)


class FileInfoAdmin(admin.ModelAdmin):
    list_display = ('i_project', 'name', 'length', 'uploaded_on')


admin.site.register(FileInfo, FileInfoAdmin)
