import glob
import json
import mimetypes
import os
from os.path import abspath, dirname
from wsgiref.util import FileWrapper
import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from stripe_payments.models import StripeType, StripeAccountMapping, PaymentMethodMapping
from stripe_payments.process import process_single_payment
from stripe_payments.utils import save_pay_method_error_log
from user_management.models import Profile, GlobalSetting
from user_management.utils import get_permission
from itrans.models import *
from loggings.utils import save_system_logs
from .utils import get_time_file, get_file_minute
from docx import Document
from .srtUtils import *
from .webvttUtils import *
from datetime import datetime


def stripe_form(request):
    return render(request, 'itrans/stripe_form.html', {})


@login_required
def file_listview(request):
    response = {'status': False, 'errors': []}
    try:
        response['headers'] = ['Job ID', 'File Name', 'Status', 'Length', 'Charge', 'Created On', 'Action']
        # response['headers'] = ['Job ID', 'File Name', 'Status', 'Length', 'Created On', 'Action']
        if request.user.is_superuser:
            file_info = FileJob.objects.all().order_by('-pk').exclude(job_status='on hold')
        else:
            file_info = FileJob.objects.filter(created_by_id=request.user.pk).exclude(job_status='on hold').order_by('-pk')
        data = []
        for file_obj in file_info:
            actions = list()
            btn_list = list()
            data_list = list()
            data_list.append([file_obj.pk, ''])
            data_list.append([file_obj.i_file.name, ''])
            # data_list.append(['Transcribed' if file_obj.job_status is True else 'Transcribing', ''])
            data_list.append([file_obj.job_status, ''])
            data_list.append([file_obj.i_file.length, ''])
            data_list.append(['$ ' + str(file_obj.charge) if file_obj.charge else "-", ''])
            data_list.append([file_obj.created_on.strftime('%Y-%m-%d %H:%M:%S'), ''])
            if file_obj.job_status == 'completed':
                view_btn = ["/itrans/get_transcribed_text/?file_id=%s" % str(file_obj.i_file.pk), "View", ""]
                btn_list.append(view_btn)
                download_btn = ["%s" % str(file_obj.i_file.pk), "Download", ""]
                btn_list.append(download_btn)
            if btn_list:
                actions.append(btn_list)
            else:
                actions.append([])
            actions.append("action")
            data_list.append(actions)
            data.append(data_list)
            response['status'] = True
            response['data'] = data
            response['page_title'] = "Jobs"
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def file_listview2(request):
    response = {'status': False, 'errors': []}
    try:
        if request.user.is_superuser:
            file_info = FileInfo.objects.all().order_by('-pk')
        else:
            file_info = FileInfo.objects.filter(i_user=request.user)
        data = []
        permissions = get_permission(request)
        if permissions is True or 'can_view_file_list' in permissions:
            for file_obj in file_info:
                data_dict = dict()
                data_dict['id'] = file_obj.pk
                data_dict['name'] = file_obj.name
                data_dict['label'] = 'Transcribed' if file_obj.status is True else 'Transcribing'
                data_dict['length'] = file_obj.length
                data_dict['uploaded'] = file_obj.uploaded_on.strftime('%Y-%m-%d')
                data_dict['transcribed_file'] = file_obj.transcribed_file.url if file_obj.transcribed_file else '-'
                data.append(data_dict)
            response['status'] = True
            response['data'] = data
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@csrf_exempt
@transaction.atomic
@login_required
def save_file(request):
    response = {'status': False, 'errors': []}
    try:
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file', None)
            filename, extension = os.path.splitext(uploaded_file.name)
            if extension not in ['.amr', '.flac', '.wav', '.ogg', '.mp3', '.mp4', '.webm']:
                response['errors'].append('Sorry! We are only accepting (amr, flac, wav, ogg, mp3, mp4, webm) file formats')
                return JsonResponse(response)
            file_info = FileInfo()
            file_info.i_user = request.user
            file_info.name = uploaded_file
            file_info.file_path = File(uploaded_file)
            file_info.save()
            # filename, extension = os.path.splitext(uploaded_file.name)
            file_path = file_info.file_path
            file_path = os.path.join(settings.MEDIA_ROOT, '%s' % file_path)
            data_dict = get_time_file(filename, extension, file_path)
            if data_dict['status']:
                length = data_dict["data"]
                file_info.length = "%s" % length
                file_info.description = data_dict['type']
                file_info.save()
                file_job = FileJob()
                file_job.i_file = file_info
                file_job.created_by = request.user
                global_setting = GlobalSetting.objects.get(name='billing_charge_per_second')
                billing_charge_per_second = global_setting.value
                charge = float(length.replace("s","")) * float(billing_charge_per_second)
                charge = str(round(charge, 2))
                file_job.charge = charge
                file_job.save()
                response['job_id'] = file_job.pk
                response['length'] = length
                response['charge'] = charge
                response['type'] = data_dict['type']
                response['status'] = 'Uploaded'
            else:
                file_info.delete()
                response['errors'].append("Problem Occur In Calculate File Length")
    except Exception as e:
        print('Exception:', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def get_file_status(request):
    response = {'status': False, 'errors': []}
    try:
        file_id = request.GET.get('file_id')
        file_obj = FileInfo.objects.get(pk=file_id)
        file_status = 'Transcribed' if file_obj.status is True else 'Transcribing'
        response['status'] = True
        response['file_status'] = file_status
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def get_confidence_level(request):
    response = {'status': False, 'errors': []}
    try:
        file_id = request.GET.get('file_id')
        file_obj = FileInfo.objects.get(pk=file_id)
        transcribed_file_meta = file_obj.transcribed_file_meta
        transcribed_file = json.load(file_obj.transcribed_file)
        response['confidence_level'] = transcribed_file_meta
        response['items'] = transcribed_file['results']['items']
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def get_transcribed_file(request):
    context = {}
    try:
        file_id = request.GET.get('file_id')
        file_obj = FileInfo.objects.get(pk=file_id)
        transcribed_file = file_obj.transcribed_file.url
        audio_file = file_obj.file_path.url
        transcribed_file_meta = json.load(file_obj.transcribed_file)
        file_type = file_obj.description
        print('file_type:', file_type)
        context['transcribed_file'] = transcribed_file
        context['audio_file'] = audio_file
        context['project_id'] = file_obj.i_project.pk
        context['type'] = file_type
        context['transcript'] = transcribed_file_meta['results']['transcripts'][0]['transcript']
        context['items'] = transcribed_file_meta['results']['items']
    except Exception as e:
        print('Exception: ', repr(e))
    return render(request, 'itrans/transcribed_file.html', context)


@login_required
def get_upload_file(request):
    resp = {'status': False}
    try:
        if request.method == 'GET':
            file_id = request.GET.get('file_id')
            file_obj = FileInfo.objects.get(pk=file_id)
            filepath = str(file_obj.file_path)
            response = StreamingHttpResponse(FileWrapper(open(filepath, 'rb')),
                                             content_type=mimetypes.guess_type(filepath)[0])
            response['Content-Disposition'] = "inline; filename= %s" % str(file_obj.file_path)
            response['Content-Length'] = os.path.getsize(filepath)
            response['Accept-Ranges'] = 'bytes'
            return response
    except Exception as e:
        print('Exception:', repr(e))
        resp['errors'] = repr(e)
    return JsonResponse(resp)


@login_required
@csrf_exempt
def edit_transcribed_file(request):
    response = {'status': False, 'errors': []}
    try:
        file_id = request.POST.get('file_id')
        items = request.POST.get('items')
        file_obj = FileInfo.objects.get(pk=file_id)
        transcribed_file_meta = json.load(file_obj.transcribed_file)
        transcribed_file_meta['results']['items'] = json.loads(items)
        json_string = json.dumps(transcribed_file_meta)
        job_obj = FileJob.objects.get(i_file=file_obj)
        filename = '%s_asrOutput.json' % job_obj.pk
        with open(filename, 'wb') as f:
            f.write(bytes(json_string.encode('utf-8')))
        file_obj.transcribed_file = File(open(filename))
        file_obj.save()
        os.remove(filename)
        response['status'] = True
    except Exception as e:
        print(repr(e), "Exception")
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def download_file(request):
    response = {'status': False, 'errors': []}
    try:
        if request.method == 'GET':
            file_format = request.GET.get('file_format')
            file_id = request.GET.get('file_id')
            file_obj = FileInfo.objects.get(pk=file_id)
            # filepath = file_obj.transcribed_file.url
            file_name, ext = os.path.splitext(file_obj.name)
            transcribed_file = json.load(file_obj.transcribed_file)
            transcript_data = transcribed_file['results']['transcripts'][0]['transcript']
            file_dir = os.path.join(settings.MEDIA_ROOT, 'itranshub/download_files/')
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir, 0o777)
            files = glob.glob('%s/*' % file_dir)
            for f in files:
                os.remove(f)
            filename = os.path.join(file_dir, '%s.txt' % file_name)
            with open(filename, 'wb') as f:
                for data in transcript_data:
                    f.write(bytes(data.encode('utf-8')))
            input_file = os.path.join(abspath(dirname(__file__)), '..%s' % file_obj.transcribed_file.url)
            if file_format == 'pdf':
                with open(filename) as file:
                    html_file = os.path.join(file_dir, '%s.html' % file_name)
                    with open(html_file, "w") as output:
                        file = file.read()
                        file = file.replace("\n", "<br>")
                        output.write(file)
                filename = os.path.join(file_dir, '%s.pdf' % file_name)
                options = {'enable-local-file-access': None}
                pdfkit.from_file(html_file, filename, options)
                download_filename = '%s.pdf' % file_name
            elif file_format == 'docx':
                doc = Document()
                with open(filename, 'r', encoding='utf-8') as openfile:
                    line = openfile.read()
                    doc.add_paragraph(line)
                    filename = os.path.join(file_dir, '%s.docx' % file_name)
                    doc.save(filename)
                download_filename = '%s.docx' % file_name
            elif file_format == 'srt':
                filename = os.path.join(file_dir, '%s.srt' % file_name)
                with open(input_file, "r") as f:
                    data = writeTranscriptToSRT(f.read(), 'en', filename)
                download_filename = '%s.srt' % file_name
            elif file_format == 'vtt':
                filename = os.path.join(file_dir, '%s.vtt' % file_name)
                with open(input_file, "r") as f:
                    data = writeTranscriptToWebVTT(f.read(), 'en', filename)
                download_filename = '%s.vtt' % file_name
            else:
                download_filename = '%s.txt' % file_name
            wrapper = FileWrapper(open(filename, 'rb'))
            response = HttpResponse(wrapper, content_type=mimetypes.guess_type(filename)[0])
            response['Content-Disposition'] = "attachment; filename=" + download_filename.replace(',', ' ')
            return response
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
        return JsonResponse(response)


@login_required
def remove_file(request):
    response = {'status': False, 'errors': []}
    try:
        file_id = request.GET.get('file_id')
        FileInfo.objects.get(pk=file_id).delete()
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def get_transcribed_file_url(request):
    response = {'status': False, 'errors': []}
    try:
        job_qs = FileJob.objects.filter(job_status=False)
        print('file_job_qs:', job_qs)
        for job_obj in job_qs:
            print("job_obj:", job_obj)
            file_obj = FileInfo.objects.get(pk=job_obj.i_file_id)
            # transcribed_file_url = get_transcribe_file_url(job_obj.pk, file_obj.file_path)
            transcribed_file_url = ''
            res = requests.get(transcribed_file_url)
            filename = '%s_asrOutput.json' % job_obj.pk
            with open(filename, 'wb') as f:
                f.write(res.content)
            file_obj.transcribed_file = File(open(filename))
            file_obj.transcribed_file_url = transcribed_file_url
            # file_obj.transcribed_file_meta = json.load(file_obj.transcribed_file)
            file_obj.save()
            job_obj.job_status = True
            job_obj.save()
            os.remove(filename)
        response['status'] = True
    except Exception as e:
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def get_transcribed_text(request):
    context = {}
    try:
        file_id = request.GET.get('file_id')
        file_obj = FileInfo.objects.get(pk=file_id)
        transcribed_file = file_obj.transcribed_file.url
        audio_file = file_obj.file_path.url
        transcribed_file_meta = json.load(file_obj.transcribed_file)
        context['transcribed_file'] = transcribed_file
        context['audio_file'] = audio_file
        context['project_id'] = file_obj.i_project.pk
        context['transcript'] = transcribed_file_meta['results']['transcripts'][0]['transcript']
        context['items'] = transcribed_file_meta['results']['items']
    except Exception as e:
        print('Exception: ', repr(e))
    return render(request, 'itrans/transcribed_text.html', context)


@login_required
@csrf_exempt
def set_job_status(request):
    response = {'status': False, 'errors': []}
    try:
        try:
            ip_address = request.META['HTTP_X_FORWARDED_FOR']
        except:
            ip_address = ''
        job_id = request.POST.get('job_id')
        job_obj = FileJob.objects.get(pk=job_id)
        pay_amt = job_obj.charge
        stripe_type_obj = StripeType.objects.all()[0]
        stripe_acc_mapping_obj = StripeAccountMapping.objects.get(i_user=request.user,i_stripe=stripe_type_obj)
        customer_stripe_ref_id = stripe_acc_mapping_obj.account_ref_id
        try:
            pay_method_mapping_obj = PaymentMethodMapping.objects.get(i_stripe_acc_mapping=stripe_acc_mapping_obj)
        except Exception as e:
            print("Exception Occurred: ", repr(e))
            response['errors'].append('Payment Method Mapping does not exist')
            return JsonResponse(response)
        stripe_payment_method_id = pay_method_mapping_obj.pay_method_ref_id
        remarks = process_single_payment(stripe_type_obj, job_obj, customer_stripe_ref_id, stripe_payment_method_id, pay_amt,
                               currency_type='usd', confirm=True)
        if remarks == 'succeeded':
            job_obj.job_status = "processing"
            job_obj.save()
            response['status'] = True
        else:
            response['status'] = False
            response['errors'].append('Payment not successful')
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        print('Status is: %s' % e.http_status)
        print('Code is: %s' % e.code)
        # param is '' in this case
        print('Param is: %s' % e.param)
        print('Message is: %s' % e.user_message)
        error_log = repr(e)
        remarks = e.user_message
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (e.user_message, repr(e))
        response['errors'].append(remarks)
    except stripe.error.RateLimitError as e:
        print("Exception Occurred: ", repr(e))
        # Too many requests made to the API too quickly
        error_log = repr(e)
        remarks = "Too many requests made to the API too quickly"
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.InvalidRequestError as e:
        print("Exception Occurred: ", repr(e))
        # Invalid parameters were supplied to Stripe's API
        error_log = repr(e)
        remarks = "Invalid parameters were supplied to Stripe's API"
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.AuthenticationError as e:
        print("Exception Occurred: ", repr(e))
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        error_log = repr(e)
        remarks = "Authentication with Stripe's API failed(maybe you changed API keys recently)"
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.APIConnectionError as e:
        print("Exception Occurred: ", repr(e))
        # Network communication with Stripe failed
        error_log = repr(e)
        remarks = "Network communication with Stripe failed"
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except stripe.error.StripeError as e:
        print("Exception Occurred: ", repr(e))
        # Display a very generic error to the user, and maybe send
        # yourself an email
        error_log = repr(e)
        remarks = "Payment Error"
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        errors = "%s | %s" % (remarks, repr(e))
        response['errors'].append(errors)
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        print("Exception Occurred: ", repr(e))
        error_log = repr(e)
        remarks = repr(e)
        save_pay_method_error_log(stripe_acc_mapping_obj, error_log, remarks, ip_address)
        response['errors'].append(repr(e))
    return JsonResponse(response)


@csrf_exempt
def upload_file(request):
    response = {'status': False, 'errors': []}
    try:
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file', None)
            filename, extension = os.path.splitext(uploaded_file.name)
            if not os.path.isdir(settings.MEDIA_ROOT + "Temp/"):
                os.makedirs(settings.MEDIA_ROOT + "Temp/", 0o777)
            fs = FileSystemStorage(location=settings.MEDIA_ROOT + "Temp/")
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = "%s_%s" % (timestamp, uploaded_file.name)
            file_path_ = fs.save(filename, uploaded_file)
            file_path = os.path.join(settings.MEDIA_ROOT + "Temp/", file_path_)
            response['file_path'] = file_path
            response['filename'] = uploaded_file.name
            data_dict = get_time_file(filename, extension, file_path)
            if data_dict['status']:
                length = data_dict["data"]
                billing_charge_per_minute = GlobalSetting.objects.get(name='billing_charge_per_minute').value
                # charge = float(length.replace("s", "")) * float(billing_charge_per_minute)
                response['file_charge_minute'] = billing_charge_per_minute
                response['file_length'] = length
                final_length = get_file_minute(length)
                charge = float(final_length) * float(billing_charge_per_minute)
                charge = str(round(charge, 2))
                response['file_charge'] = charge
                response['file_min'] = final_length
                response['closed_captioning_services'] = GlobalSetting.objects.get(
                    name="closed_captioning_services").value
                response['rush_my_order'] = GlobalSetting.objects.get(name="rush_my_order").value
                response['instant_first_draft'] = GlobalSetting.objects.get(name="instant_first_draft").value
                response['on_speaker_change'] = GlobalSetting.objects.get(name="on_speaker_change").value
                response['every_2_minutes'] = GlobalSetting.objects.get(name="every_2_minutes").value
                response['verbatim'] = GlobalSetting.objects.get(name="verbatim").value
                response['status'] = True
                # print('resp:', response)
            else:
                response['errors'].append('Not supported file format')
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def projects_file_list(request):
    template = 'itrans/projects_file_list.html'
    return render(request, template, {})


@login_required
def projects_file_listview(request):
    response = {'status': False, 'errors': []}
    try:
        project_id = request.GET.get('project_id', None)
        response['page_title'] = "Files"
        response['headers'] = ['File ID', 'File Name', 'Status', 'Length', 'Charge', 'Created On', 'Action']
        file_info = FileInfo.objects.filter(i_project_id=project_id)
        data = []
        for file_info_obj in file_info:
            file_obj = FileJob.objects.get(i_file=file_info_obj)
            actions = list()
            btn_list = list()
            data_list = list()
            data_list.append([file_info_obj.pk, ''])
            data_list.append([file_obj.i_file.name, ''])
            data_list.append([file_obj.job_status, ''])
            data_list.append(["%s min (%s)" % (get_file_minute(file_obj.i_file.length), file_obj.i_file.length), ''])
            # data_list.append([file_obj.i_file.length, ''])
            data_list.append(['$ ' + str(file_obj.charge) if file_obj.charge else "-", ''])
            data_list.append([file_obj.created_on.strftime('%Y-%m-%d %H:%M:%S'), ''])
            if file_obj.job_status == 'completed':
                view_btn = ["/itrans/get_transcribed_text/?file_id=%s" % str(file_obj.i_file.pk), "View", ""]
                btn_list.append(view_btn)
                download_btn = ["%s" % str(file_obj.i_file.pk), "Download", ""]
                btn_list.append(download_btn)
            if btn_list:
                actions.append(btn_list)
            else:
                actions.append([])
            actions.append("action")
            data_list.append(actions)
            data.append(data_list)
            response['status'] = True
            response['data'] = data
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)


@login_required
def project_listview(request):
    response = {'status': False, 'errors': []}
    try:
        response['page_title'] = "Projects"
        response['headers'] = ['Project ID', 'Project Name', 'Total Files', 'Total Length', 'Total Charge', 'Created On', 'Action']
        columns = ['pk', 'name', 'total_length', 'total_charge', 'created_on']
        if request.user.is_superuser:
            project_qs = Project.objects.all().values_list(*columns).order_by('-pk')
        else:
            project_qs = Project.objects.filter(created_by=request.user).values_list(*columns).order_by('-pk')
        data = []
        for project_obj in project_qs:
            actions = list()
            btn_list = list()
            data_list = list()
            data_list.append([project_obj[0], ''])
            data_list.append([project_obj[1], ''])
            data_list.append([FileInfo.objects.filter(i_project_id=project_obj[0]).count(), ''])
            data_list.append(["%s min" % project_obj[2], ''])
            data_list.append(['$ ' + str(project_obj[3]) if project_obj[3] else "-", ''])
            data_list.append([project_obj[4].strftime('%Y-%m-%d %H:%M:%S'), ''])
            view_btn = ["/itrans/projects_file_list/?project_id=%s" % str(project_obj[0]), "View Files", ""]
            btn_list.append(view_btn)
            payment_btn = ["/stripe_payments/invoice_payment_list/?project_id=%s" % str(project_obj[0]), "View Invoice Payments", ""]
            btn_list.append(payment_btn)
            view_invoice_btn = ["%s" % str(project_obj[0]), "View Invoice", ""]
            btn_list.append(view_invoice_btn)
            if btn_list:
                actions.append(btn_list)
            else:
                actions.append([])
            actions.append("action")
            data_list.append(actions)
            data.append(data_list)
        response['status'] = True
        response['data'] = data
    except Exception as e:
        print('Exception: ', repr(e))
        response['errors'].append(repr(e))
    return JsonResponse(response)
