from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User, Group

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with complete details."""
    
    email = forms.EmailField(required=True, help_text="Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter first name.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Enter last name.")
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="User Role")
    is_active = forms.BooleanField(required=False, initial=True, help_text="Designates whether this user should be treated as active.")
    is_staff = forms.BooleanField(required=False, help_text="Designates whether the user can log into this admin site.")
    is_superuser = forms.BooleanField(required=False, help_text="Designates that this user has all permissions without explicitly assigning them.")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser']


class CustomUserUpdateForm(forms.ModelForm):
    """Form for editing existing users with all fields."""
    
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Enter a new password if you want to change it.")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Enter the new password again for confirmation.")
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="User Role")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            self.add_error('password2', "The two password fields must match.")

        return cleaned_data

class CustomUserProfileForm(forms.ModelForm):
    """Form for users to update their own profile and change password."""
    
    old_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Current Password", help_text="Enter your current password.")
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password", help_text="Enter a new password if you want to change it.")
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password", help_text="Enter the new password again for confirmation.")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'old_password', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if not self.instance.check_password(old_password):
                self.add_error('old_password', "The current password is incorrect.")
            if password1 and password1 != password2:
                self.add_error('password2', "The two password fields must match.")

        return cleaned_data