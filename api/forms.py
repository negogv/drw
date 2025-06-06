from django import forms
from .models import TheUser, Employer, Employee, Country, City
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.validators import RegexValidator


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

    name = forms.CharField(max_length=300)
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select a country"
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),  # TODO: make a mechanism to check cities by chosen country
        empty_label="Select a city"
    )
    text = forms.CharField(max_length=400, widget=forms.TextInput(attrs={'placeholder': 'Tell us more about you!'}),
                           required=False)
    media_array = forms.CharField(max_length=80)  # TODO: media mechanism


class EmployeeRegistrationForm(forms.Form):
    class Meta:
        model = Employee
        fields = ['country', 'city', 'phone', 'email', 'text', 'cv', 'media_array']

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select a country"
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="Select a city"
    )
    # phone = forms.CharField(
    #     max_length=20,
    #     validators=[
    #         RegexValidator(
    #             regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
    #             message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    #     ]
    # )
    phone = forms.CharField(max_length=20, required=True, label="Contact phone")
    email = forms.EmailField(required=True, label='Contact email')
    text = forms.CharField(max_length=400,
                           widget=forms.TextInput(attrs={'placeholder': 'Tell us more about you!'}),
                           required=False)
    media_array = forms.CharField(max_length=80)
    cv = forms.FileField(allow_empty_file=True, required=False)


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

