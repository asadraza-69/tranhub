from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from user_management.models import *


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['password', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A User with that Email already exists.")
        return email.lower()


class UserUpdateForm(ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

    def clean_email(self):
        email = self.cleaned_data['email']
        user_email = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if user_email:
            raise forms.ValidationError('A user with that email already exists.')
        return email.lower()


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']
#         exclude = ('user', 'qr_verified', 'permission_tags', 'permission_groups', 'i_company', 'joining_date', 'end_trial_date', 'is_trial_active')


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name']
