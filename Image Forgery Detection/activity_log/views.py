import io
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import get_template
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from case_management.models import Case
from .models import ActivityLog

@login_required
def activity_log_list(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')
    users = User.objects.all()
    cases = Case.objects.all()

    # Apply user filter
    user_filter = request.GET.get('user')
    if user_filter and user_filter != 'None':
        logs = logs.filter(user__id=user_filter)

    # Apply case filter
    case_filter = request.GET.get('case')
    if case_filter and case_filter != 'None':
        logs = logs.filter(case__id=case_filter)

    return render(request, 'activity_log/activity_log_list.html', {
        'logs': logs,
        'users': users,
        'cases': cases,
        'user_filter': user_filter,
        'case_filter': case_filter,
    })

@login_required
def download_logs_pdf(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')

    # Apply user filter
    user_filter = request.GET.get('user')
    if user_filter and user_filter != 'None':
        try:
            logs = logs.filter(user__id=int(user_filter))
        except ValueError:
            return HttpResponseBadRequest("Invalid user ID")

    # Apply case filter
    case_filter = request.GET.get('case')
    if case_filter and case_filter != 'None':
        try:
            logs = logs.filter(case__id=int(case_filter))
        except ValueError:
            return HttpResponseBadRequest("Invalid case ID")

    template = get_template('activity_log/logs_pdf.html')
    html = template.render({'logs': logs})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activity_logs.pdf"'

    HTML(string=html).write_pdf(response)
    return response
