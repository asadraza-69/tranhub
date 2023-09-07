import json
import os
import requests
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from itrans.models import FileJob, FileInfo


class Command(BaseCommand):
    help = 'transcribe file'

    def handle(self, *args, **options):
        job_qs = FileJob.objects.filter(job_status="processing")
        print('file_job_qs:', job_qs)
        for job_obj in job_qs:
            print("job_obj:", job_obj)
            try:
                file_obj = FileInfo.objects.get(pk=job_obj.i_file_id)
                file_path = file_obj.file_path.url
                file_name = os.path.basename(file_path)
                url = "%s/%s/%s/" % (settings.PROCESS_JOB_API_URL, job_obj.pk, file_name)
                api_response = requests.get(url)
                api_url = "%s/%s/" % (settings.JOB_STATUS_API_URL, job_obj.pk)
                transcribed_file_url = requests.get(api_url)
                res = requests.get(transcribed_file_url.content)
                filename = '%s_asrOutput.json' % job_obj.pk
                with open(filename, 'wb') as f:
                    f.write(res.content)
                file_obj.transcribed_file = File(open(filename))
                file_obj.save()
                job_obj.job_status = "completed"
                job_obj.remarks = 'Successfully transcribe'
                job_obj.save()
                os.remove(filename)
                self.stdout.write(self.style.SUCCESS('Successfully transcribe file "Job ID:%s"' % job_obj.pk))
            except Exception as e:
                print('Exception:', repr(e))
                job_obj.remarks = repr(e)
                job_obj.save()
