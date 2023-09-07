from loggings.models import SystemLogs
from user_management.models import Profile
from django.utils import timezone


def save_system_logs(action_desc, user_name):
    try:
        profile = Profile.objects.get(user__username=user_name)
        SystemLogs(**{'action_by': user_name, 'action_desc': action_desc,
                      'action_by_id': profile.user.id, 'action_date': timezone.localtime(timezone.now())}).save()
    except Profile.DoesNotExist as e:
        print(e)


def system_logs_listview_func(request):
    response = {}
    response['headers'] = ['User', 'User ID', 'Activity on', 'Description']
    log_msg = "%s Visited the System Logs Page" % request.user.username
    save_system_logs(log_msg, request.user.username)
    from user_management.utils import get_permission
    permissions = get_permission(request)
    if permissions == True or "can_view_system_logs" in permissions:
        rows = []
        if request.method == 'GET':
            columns = ['action_by', 'action_by_id', 'action_date', 'action_desc']
            system_logs_vs = SystemLogs.objects.values_list(*columns).order_by('-pk')
            for  action_by, action_by_id, action_date, action_desc in system_logs_vs:
                row = list()
                row.append([action_by, ''])
                row.append([action_by_id, ''])
                row.append(
                    [action_date.strftime('%B %d, %Y - %H:%M:%S') if action_date else '-', ''])
                row.append([action_desc, ''])
                rows.append(row)
    response['data'] = rows
    response['page_title'] = "System Logs"
    response['page_list_title'] = " "
    response['model_name'] = ""
    response['breadcrums'] = ""
    return response

