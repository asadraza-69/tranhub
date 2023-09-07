from django.conf.urls import url, include
from django.urls import path

from .views import *


urlpatterns = [
    path('file_listview2/', file_listview2, name='file_listview2'),
    path('file_listview/', project_listview, name='file_listview'),
    path('save_file/', save_file, name='save_file'),
    path('get_file_status/', get_file_status, name='get_file_status'),
    path('get_confidence_level/', get_confidence_level, name='get_confidence_level'),
    path('get_transcribed_file/', get_transcribed_file, name='get_transcribed_file'),
    path('get_transcribed_text/', get_transcribed_text, name='get_transcribed_text'),
    path('edit_transcribed_file/', edit_transcribed_file, name='edit_transcribed_file'),
    path('download_file/', download_file, name='download_file'),
    path('remove_file/', remove_file, name='remove_file'),
    path('stripe_form/', stripe_form, name='stripe_form'),
    path('get_transcribed_file_url/', get_transcribed_file_url, name='get_transcribed_file_url'),
    path('set_job_status/', set_job_status, name='set_job_status'),
    path('get_upload_file/', get_upload_file, name='get_upload_file'),
    path('upload_file/', upload_file, name='upload_file'),
    path('projects_file_listview/', projects_file_listview, name='projects_file_listview'),
    path('projects_file_list/', projects_file_list, name='projects_file_list'),
    # path('project_listview/', project_listview, name='project_listview'),

]
