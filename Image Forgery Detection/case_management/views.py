from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Case
from image_verification.models import CaseImage
from .forms import CaseForm
from activity_log.models import log_activity
from user_management.decorators import group_required

# List all cases
@login_required
@group_required('Viewer')
def case_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    cases = Case.objects.all().order_by('-created_at')
    
    if search_query:
        cases = cases.filter(case_name__icontains=search_query)
    
    if status_filter:
        cases = cases.filter(status=status_filter)
    
    return render(request, 'case_management/case_list.html', {'cases': cases, 'status_filter': status_filter})

# Create a new case
@login_required
@group_required('Admin')
def case_create(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.created_by = request.user
            case.save()
            log_activity(request.user, 'Created case', case=case)
            return redirect('case_list')
    else:
        form = CaseForm()
    return render(request, 'case_management/case_form.html', {'form': form})

# Update an existing case
@login_required
@group_required('Admin')
def case_update(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Updated case', case=case)
            return redirect('case_list')
    else:
        form = CaseForm(instance=case)
    return render(request, 'case_management/case_form.html', {'form': form})

# Delete a case
@login_required
@group_required('Admin')
def case_delete(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.method == 'POST':
        case.delete()
        log_activity(request.user, 'Deleted case', case=case)
        return redirect('case_list')
    return render(request, 'case_management/case_confirm_delete.html', {'case': case})

# Case detail view
@login_required
@group_required('Viewer')
def case_detail(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    images = CaseImage.objects.filter(case=case)
    return render(request, 'case_management/case_detail.html', {'case': case, 'images': images})