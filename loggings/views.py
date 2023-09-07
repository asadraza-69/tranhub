from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
import json

# Create your views here.
from loggings.utils import save_system_logs, system_logs_listview_func


@login_required
def system_logs_list(request):
    return render(request, 'loggings/system_logs_list.html/', {})


@login_required
def system_logs_listview(request):
    response = system_logs_listview_func(request)
    return HttpResponse(json.dumps(response))
