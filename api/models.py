from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser
from django.core.validators import RegexValidator


class TheUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        COMPANY = 'company'
        EMPLOYEE = 'employee'
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        help_text="Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={"unique": "A user with that username already exists."}
    )
    phone = models.CharField(max_length=20,
                             validators=[
                                 RegexValidator(
                                     regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
                                     message="Phone number must be entered in the format: '+000123456789'. "
                                             "Up to 15 digits allowed.")
                             ]
                             )
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    user_permissions = None
    groups = None
    email = models.EmailField("email address")
    role = models.CharField(max_length=8, choices=RoleChoices.choices)

    def __str__(self):
        return "{}".format(self.username)


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(TheUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField("email address")
    country = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    text = models.TextField(null=True)
    media = models.ManyToManyField('MediaFile')
    vacancies = models.ManyToManyField("Vacancy")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(TheUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    phone = models.CharField(max_length=25)
    email = models.EmailField("email address")
    text = models.TextField(max_length=400, null=True)
    media = models.ManyToManyField('MediaFile')
    cv = models.ForeignKey("CV", on_delete=models.SET_NULL, null=True)
    skills = models.ManyToManyField(Skill)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return TheUser.objects.get(id=self.user).first_name + TheUser.objects.get(id=self.user)
        return self.name


class Vacancy(models.Model):
    class SalaryTypeChoices(models.TextChoices):
        YEAR = 'year'
        MONTH = 'month'
        HOUR = 'hour'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(Company, on_delete=models.CASCADE)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    text = models.TextField(null=True)
    salary = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.SET(1))
    salary_type = models.CharField(max_length=5, choices=SalaryTypeChoices.choices)
    media = models.ManyToManyField('MediaFile')
    tags = models.ManyToManyField(Skill)
    is_online = models.BooleanField(default=False)
    respondents = models.ManyToManyField(Employee)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CV(models.Model):
    id = models.AutoField(primary_key=True)
    binary = models.BinaryField()
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class MediaFile(models.Model):
    id = models.AutoField(primary_key=True)
    binary = models.BinaryField()
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
