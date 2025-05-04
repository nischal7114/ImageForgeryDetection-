from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomUserProfileForm
from .decorators import group_required
from activity_log.models import log_activity

@login_required
@group_required('Admin')
def user_list(request):
    """ Display all users with filtering & search"""
    users = User.objects.all()
    roles = Group.objects.all()

    # Apply filtering based on selected role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(groups__name=role_filter)

    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(username__icontains=search_query)

    return render(request, 'user_management/user_list.html', {'users': users, 'roles': roles})

@login_required
@group_required('Admin')
def user_create(request):
    """ Admin Creates Users & Assigns Roles."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Hash password
            user.save()

            # Assign the selected role (group)
            role = form.cleaned_data['role']
            if role:
                user.groups.add(role)

            log_activity(request.user, 'Created user', case=None, details=f'User: {user.username}')
            messages.success(request, "User created successfully!")
            return redirect('user_list')
        else:
            messages.error(request, "Error creating user. Please check the details.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'user_management/user_form.html', {'form': form})

@login_required
@group_required('Admin')
def user_edit(request, user_id):
    """ Admin Edits User Details & Role"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)

            # Handle password change
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)

            # Assign updated role
            role = form.cleaned_data.get('role')
            user.groups.clear()  # Remove previous roles
            if role:
                user.groups.add(role)

            user.save()
            log_activity(request.user, 'Edited user', case=None, details=f'User: {user.username}')
            messages.success(request, "User updated successfully!")
            return redirect('user_list')  # Redirect to user list page
        else:
            messages.error(request, "Error updating user. Please check the details.")
    else:
        form = CustomUserUpdateForm(instance=user, initial={'role': user.groups.first()})

    return render(request, 'user_management/user_form.html', {'form': form, 'edit': True})

@login_required
@group_required('Admin')
def user_deactivate(request, user_id):
    """ Deactivate a user (Soft Delete)."""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = False
        user.save()
        log_activity(request.user, 'Deactivated user', case=None, details=f'User: {user.username}')
        messages.success(request, f"User {user.username} has been deactivated!")
        return redirect('user_list')

    return render(request, 'user_management/user_confirm_deactivate.html', {'user': user})

@login_required
@group_required('Admin')
def user_activate(request, user_id):
    """Reactivate a user."""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = True
        user.save()
        log_activity(request.user, 'Activated user', case=None, details=f'User: {user.username}')
        messages.success(request, f"User {user.username} has been reactivated!")
        return redirect('user_list')

    return render(request, 'user_management/user_confirm_activate.html', {'user': user})

@login_required
def user_profile(request):
    """ User Profile Update View"""
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            # Handle password change
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
                update_session_auth_hash(request, user)  # Important to keep the user logged in

            user.save()
            log_activity(request.user, 'Updated profile', case=None)
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect back to profile page
        else:
            messages.error(request, "Error updating profile. Please check your input.")
    else:
        form = CustomUserProfileForm(instance=request.user)

    return render(request, 'user_management/profile.html', {'form': form})

@login_required
def dashboard(request):
    is_admin_or_superuser = request.user.is_superuser or request.user.groups.filter(name='Admin').exists()
    return render(request, 'user_management/dashboard.html', {'is_admin_or_superuser': is_admin_or_superuser})