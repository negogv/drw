from django import forms
from .models import TheUser, Employer, Employee, Country, City
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import BaseUserCreationForm


class PositionTitleFilterForm(forms.Form):
    title = forms.CharField()


class RegistrationForm(BaseUserCreationForm):
    class Meta:
        model = TheUser
        fields = ["username", "first_name", "last_name", 'role', "email", "phone", "password1", "password2"]
    username = forms.CharField(max_length=30)
    role = forms.ChoiceField(choices=TheUser.RoleChoices.choices)
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


class EmployerRegistrationForm(forms.Form):
    class Meta:
        model = Employer
        fields = ['name', 'country', 'city', 'text', 'media_array']

    name = forms.CharField(max_length=300, help_text='Keep it empty to have make your name and surname '
                                                     'as a name for employer profile', empty_value='mat jebal')
    # TODO: doesnt let to leave a field empty
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select a country"
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),  # TODO: make a mechanism to check cities by chosen country
        empty_label="Select a city"
    )
    text = forms.CharField(max_length=400, widget=forms.TextInput(attrs={'placeholder': 'Tell us more about you!'}))
    media_array = forms.CharField(max_length=80)  # TODO: media mechanism


class EmployeeRegistrationForm(forms.Form):
    class Meta:
        model = Employee
        fields = ['country', 'city', 'text', 'media_array']

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select a country"
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="Select a country first"
    )
    text = forms.CharField(max_length=400,
                           widget=forms.TextInput(attrs={'placeholder': 'Tell us more about you!'}))
    media_array = forms.CharField(max_length=80)
    cv = forms.FileField(allow_empty_file=True)


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

