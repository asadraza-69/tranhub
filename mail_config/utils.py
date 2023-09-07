from django.core.mail import get_connection
from django.core.mail import send_mail,EmailMessage

from mail_config.forms import EmailForm
from mail_config.models import SendEmail



def send_email_func(send_email_obj, subject, users_list=[], attachment=None, body_text=None, html_message=None):
    response = 0
    email = send_email_obj.email
    password = send_email_obj.password
    email_host = send_email_obj.host
    port = int(send_email_obj.port)
    connection = get_connection(host=email_host,
                                port=port,
                                username=email,
                                password=password,
                                use_tls=True)

    response = send_mail(subject, body_text, email, users_list, connection=connection, html_message=html_message)
    return response


def send_email_attachment(send_email_obj, subject, users_list=[], attachment=None, body_text=None, html_message=None):
    response = 0
    email = send_email_obj.email
    password = send_email_obj.password
    email_host = send_email_obj.host
    port = int(send_email_obj.port)
    connection = get_connection(host=email_host,
                                port=port,
                                username=email,
                                password=password,
                                use_tls=True)

    response = EmailMessage(subject, body_text, email, users_list, connection=connection)
    if attachment:
        response.attach_file(attachment)
    response.content_subtype = 'html'
    final_response = response.send()
    return final_response

def email_settings_list_view_func(request):
    from user_management.utils import get_permission
    permissions = get_permission(request)
    response = {'data': None}
    if permissions == True or 'can_view_email_setting_list' in permissions:
        headers = ['Title', 'Email', 'Host', 'Category', 'Port', 'Port Type', 'Time Out', 'Action']
        response['headers'] = headers
        columns = ['pk', 'title', 'email', 'host', 'category', 'port', 'port_type', 'timeout']
        send_email_settings = SendEmail.objects.values_list(*columns)
        data =[]
        for pk,title,email,host,category,port,port_type,time_out in send_email_settings:
            datum = list()
            actions = list()
            btn_list = list()
            datum.append([title, ''])
            datum.append([email, ''])
            datum.append([host, ''])
            datum.append([category, ''])
            datum.append([port, ''])
            datum.append([port_type, ''])
            datum.append([time_out, ''])

            if permissions == True or 'can_edit_email_settings' in permissions:
                edit_btn = ["/mail_config/edit_email_settings/update/" + str(pk) + "", "Edit", ""]
                btn_list.append(edit_btn)
            if btn_list:
                actions.append(btn_list)
            else:
                actions.append([])
            actions.append("action")
            datum.append(actions)
            data.append(datum)
        response['data'] = data
        response['page_title'] = "Email Settings"
        response['page_list_title'] = "Email Settings List View"
        response['model_name'] = ""
        response['breadcrums'] = ""
        return response


def update_email_settings_func(request, setting_id):
    response = {}
    send_mail_obj = SendEmail.objects.get(pk=setting_id)
    email_form = EmailForm(request.POST,instance=send_mail_obj)
    if email_form.is_valid():
        try:
            email_form = email_form.save()
            response['status'] = True
        except Exception as e:
            print (e)
            response['status'] = False

    return response
