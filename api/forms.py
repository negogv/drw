from django import forms
from .models import TheUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import BaseUserCreationForm


class PositionTitleFilterForm(forms.Form):
    title = forms.CharField()


class RegistrationForm(BaseUserCreationForm):
    class Meta:
        model = TheUser
        fields = ["username", "first_name", "last_name", "email", "phone", "password1", "password2"]
    username = forms.CharField(max_length=30)
    password1 = forms.CharField(
        label='Password',
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label='Password confirmation',
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    # email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=20, required=True)
    # last_name = forms.CharField(max_length=30)


class LoginForm(forms.Form):
    class Meta:
        model = TheUser
        fields = ['username', 'password']
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

