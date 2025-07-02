from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import BaseUserCreationForm
from django.core.validators import RegexValidator


class VacancyTitleFilterForm(forms.Form):
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


class CompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'country', 'state', 'city', 'text', 'media']

    name = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'placeholder': 'Name for a company'}))

    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Contact mobile number',
                                      'class': 'form-control'})
    )

    email = forms.EmailField(required=True,
                             label='Contact email',
                             widget=forms.TextInput(attrs={'placeholder': 'your.email@example.com',
                                                           'class': 'form-control'}))

    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'country-input',
                                      'autocomplete': 'off',
                                      'name': 'country',
                                      'placeholder': 'Select a country'})
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'state-input',
                                      'autocomplete': 'off',
                                      'name': 'state',
                                      'placeholder': 'Select a state'})
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'city-input',
                                      'autocomplete': 'off',
                                      'name': 'city',
                                      'placeholder': 'Select a city'})
    )

    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control',
                                                                        'placeholder':
                                                                        'Tell us more about your enterprise!'}),
                           required=False)

    media = forms.CharField(max_length=80, required=False)


class EmployeeRegistrationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['country', 'state', 'city', 'phone', 'email', 'text', 'skills', 'cv']

    media = forms.CharField(required=False)

    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'country-input',
                                      'autocomplete': 'off',
                                      'name': 'country',
                                      'placeholder': 'Select a country'})
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'state-input',
                                      'autocomplete': 'off',
                                      'name': 'state',
                                      'placeholder': 'Select a state'})
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'city-input',
                                      'autocomplete': 'off',
                                      'name': 'city',
                                      'placeholder': 'Select a city'})
    )
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        ],
        widget=forms.TextInput(attrs={'placeholder': '+123456789012',
                                      'class': 'form-control'})
    )

    email = forms.EmailField(required=True,
                             label='Contact email',
                             widget=forms.TextInput(attrs={'placeholder': 'your.email@example.com',
                                                           'class': 'form-control'}))

    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell us more about you!',
                                                        'class': 'form-control',
                                                        'rows': '5',
                                                        'style': "height: unset;"}),
                           required=False)
    skills = forms.CharField(required=False)
    cv = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginForm(forms.Form):
    class Meta:
        model = TheUser
        fields = ['username', 'password']
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True,
                                                             'class': 'form-control'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          'class': 'form-control'})
    )


class NewVacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'text', 'country', 'city', 'salary', 'currency', 'salary_type', 'media', 'tags']
    title = forms.CharField(max_length=200,
                            widget=forms.TextInput(attrs={'placeholder': 'Name of the vacancy',
                                                          'class': 'form-control'}),
                            required=True)
    text = forms.CharField(widget=forms.Textarea(attrs={"rows": "5",
                                                        'placeholder': 'More about the vacancy',
                                                        'class': 'form-control'}))
    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'country-input',
                                      'autocomplete': 'off',
                                      'name': 'country',
                                      'placeholder': 'Select a country'})
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'state-input',
                                      'autocomplete': 'off',
                                      'name': 'state',
                                      'placeholder': 'Select a state'})
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-select',
                                      'id': 'city-input',
                                      'autocomplete': 'off',
                                      'name': 'city',
                                      'placeholder': 'Select a city'})
    )
    salary = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Name of the vacancy',
                                                              'class': 'form-control'}),
                                required=True)
    currency = forms.ModelChoiceField(queryset=Currency.objects.exclude(id=1),
                                      empty_label="Select a currency",
                                      to_field_name='code',
                                      widget=forms.Select(attrs={'class': 'form-select',
                                                                 'placeholder': 'Select a currency'}))
    salary_type_choices = (('year', 'Year'),
                           ('month', 'Month'),
                           ('hour', 'Hour'))
    salary_type = forms.ChoiceField(choices=salary_type_choices,
                                    widget=forms.Select(attrs={'class': 'form-select'}))
    media = forms.CharField(required=False)
    tags = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

