from django import forms
from django.forms import ModelForm
from mail_config.models import SendEmail

class EmailForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = SendEmail
        fields = ['title', 'email', 'password', 'confirm_password', 'host', 'category', 'port', 'port_type', 'timeout']
