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


class Company(models.Model):       # TODO: Maybe add blank=True to unnecessary fields?
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(TheUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, unique=True)
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
    cv = models.FileField(null=True, editable=True)
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


# class VacancyFeedback(models.Model):  # TODO: Fuck this shit
#     id = models.AutoField(primary_key=True)
#     owner = models.ForeignKey(Company, on_delete=models.CASCADE)
#     vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
#     feedback_type = models.CharField(max_length=30)
#     file = models.BinaryField(null=True)
#     text = models.TextField(null=True)
#     created = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.vacancy


class MediaFile(models.Model):
    id = models.AutoField(primary_key=True)
    binary = models.BinaryField()
    name = models.CharField(max_length=250)
    # TODO:  the concept is next: save image to temporary dir, convert image to bytes and save to BLOB,
    # TODO:  delete the image. Media_name stays for media name even it is ImageField
    # FIXME:        WOW THERE IS NO FUCKING NEED IN IT, JUST KEEP IT

    def __str__(self):
        return self.name
