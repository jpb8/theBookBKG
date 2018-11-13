from django import forms
from django.contrib.auth.models import User
from account.models import Account


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class AccountInfoForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('profile_pic',)


