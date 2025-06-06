from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser


class TheUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        EMPLOYER = 'employer'
        EMPLOYEE = 'employee'
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        help_text="Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={"unique": "A user with that username already exists."}
    )
    phone = models.CharField(max_length=20)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    user_permissions = None
    groups = None
    email = models.EmailField("email address")
    role = models.CharField(max_length=8, choices=RoleChoices.choices)

    def __str__(self):
        return "{}".format(self.username)


class Employer(models.Model):       # TODO: Maybe add blank=True to unnecessary fields?
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    text = models.TextField(null=True)
    media_array = models.CharField(max_length=80, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    phone = models.IntegerField(null=True)  # TODO: checkpoint if the user wants to remain the same number/email
    email = models.CharField(max_length=40, null=True)  # TODO: for the others as for registration
    text = models.TextField(max_length=400, null=True)
    media_array = models.CharField(max_length=80, null=True)
    cv = models.FileField(null=True, editable=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    class SalaryTypeChoices(models.TextChoices):
        YEAR = 'Y'
        MONTH = 'M'
        HOUR = 'H'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(Employer, on_delete=models.CASCADE)
    text = models.TextField()
    salary = models.IntegerField()
    salary_type = models.CharField(max_length=1, choices=SalaryTypeChoices.choices)
    media_array = models.CharField(max_length=130, null=True)
    tags = models.CharField(max_length=150, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class PositionFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Employer, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=30)
    file = models.BinaryField(null=True)
    text = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.position


class MediaFile(models.Model):
    id = models.AutoField(primary_key=True)
    media = models.BinaryField()
    media_name = models.CharField(max_length=15)
    # TODO:  the concept is next: save image to temporary dir, convert image to bytes and save to BLOB,
    # TODO:  delete the image. Media_name stays for media name even it is ImageField
    # FIXME:        WOW THERE IS NO FUCKING NEED IN IT, JUST KEEP IT

    def __str__(self):
        return self.media_name


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2)  # ISO country code

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.country}"


class TestImage(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField()
