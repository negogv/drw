import copy
import requests
from django.shortcuts import render, redirect, get_object_or_404
import mysql.connector
from django.http import HttpResponse, JsonResponse
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import generics, viewsets, status
# from .models import *
from . import serializers
import api.models
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
import os.path as path
from .forms import RegistrationForm, LoginForm, EmployeeRegistrationForm, CompanyRegistrationForm, NewVacancyForm
# Create your views here.

from django.contrib.auth.forms import UserCreationForm

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='34679o',
    database='derrotewaschbaer',
    autocommit=True
)

cursor = db.cursor(buffered=True)


class CompanyViews:
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyListCreate(CompanyViews, generics.ListCreateAPIView):
    pass


class CompanyRetrieveUpdateDestroy(CompanyViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class EmployeeViews:
    queryset = Employee.objects.all()
    serializer_class = CompanySerializer


class EmployeeListCreate(EmployeeViews, viewsets.ModelViewSet):
    # Just for interest to learn how to create a model in django by hands

    def list(self, request, *args, **kwargs):
        queryset = Employee.objects.all()
        serializer_class = EmployeeSerializer(instance=queryset, many=True)
        return Response(data=serializer_class.data, status=200)

    def create(self, request, *args, **kwargs):
        serializer = EmployeeSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeeRetrieveUpdateDestroy(EmployeeViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class VacancyViews:
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class VacancyListCreate(VacancyViews, generics.ListCreateAPIView):
    pass


class VacancyRetrieveUpdateDestroy(VacancyViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class VacancyListByTags(APIView):
    def get(self, request: Request, **kwargs):
        instance = Vacancy.objects.filter(tags__contains=kwargs['tag'])
        serializer = VacancySerializer(instance, many=True)

        return Response(serializer.data)


class VacancyListBySalary(generics.ListAPIView):
    serializer_class = VacancySerializer

    def get_queryset(self):
        minimum = self.request.query_params.get('min-salary', 0)
        maximum = self.request.query_params.get('max-salary', 2147483647)
        return Vacancy.objects.filter(salary__gte=minimum).filter(salary__lte=maximum)


class ModelSearchList(APIView):
    # TODO: This view should search for a model by its parameters
    def get(self, request: Request, **kwargs):
        min_salary = request.query_params.get('min-salary')
        max_salary = request.query_params.get('max-salary')
        name = request.query_params.get('name')
        salary_type = request.query_params.get('salary-type')

        model_name = kwargs['model'].capitalize()
        instance = getattr(api.models, model_name).objects\
            .filter(salary__gte=min_salary)\
            .filter(salary__lte=max_salary).filter(salary_type__in=salary_type)




class FeedbackViews:
    queryset = VacancyFeedback.objects.all()
    serializer_class = VacancyFeedbackSerializer


class FeedbackListCreate(FeedbackViews, generics.ListCreateAPIView):
    pass


class FeedbackRetrieveUpdateDestroy(FeedbackViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class RetrieveMediaArray(APIView):
    def get(self, request, **kwargs):
        model_name = kwargs['model'].capitalize()  # To which class should we attach new mediafile
        instance = getattr(api.models, model_name).objects.get(id=kwargs['pk'])

        media_array = instance.media_array.split(', ')

        return Response(media_array, status=status.HTTP_200_OK)


class MediaFileCreate(APIView):
    parser_classes = (MultiPartParser, FormParser)  # FIXME do i really need this line?

    @staticmethod
    def create_mediafile(file: TemporaryUploadedFile) -> int:
        """
        Takes an image in format TemporaryUploadedFile, saves in api_mediafile table and returns new-created primary key
        """
        with transaction.atomic():
            binary_data = b''.join(chunk for chunk in file.chunks())
            media_file = MediaFile.objects.create(
                media=binary_data,
                media_name=file.name
            )

        return media_file.id

    def post(self, request, **kwargs):
        # TODO: nehm die ganze Funktion ins try-loop um instance.media_array error zu vermeiden, wenn modell hat kein media_array Feld
        file_obj: TemporaryUploadedFile = request.data.get('file')
        if file_obj:
            model_name = kwargs['model'].capitalize()  # To which class should we attach new mediafile
            instance = getattr(api.models, model_name).objects.get(id=kwargs['pk'])

            media_id = self.create_mediafile(file_obj)

            media_array = instance.media_array

            if media_array:
                model_serializer_data = {'media_array': media_array + f", {str(media_id)}"}
            else:
                model_serializer_data = {'media_array': str(media_id)}

            serializer = getattr(api.serializers, model_name + 'Serializer')(instance,
                                                                             data=model_serializer_data,
                                                                             partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):
        """
        returns an array of media files ids of certain model
        """
        model_name = kwargs['model'].capitalize()  # To which class should we attach new mediafile
        instance = getattr(api.models, model_name).objects.get(id=kwargs['pk'])

        media_array = instance.media_array.split(', ')

        return Response(media_array, status=status.HTTP_200_OK)


class MediaFileRetrieve(APIView):
    def get(self, request, **kwargs):
        """
        Returns a response with an image that was saved in MediaFile with primary key "kwargs['pk']"
        Uncomment first from return or second from return line to display image in browser or download, respectively
        """
        instance = MediaFile.objects.get(id=kwargs['pk'])

        image_type = instance.media_name.split('.')[-1]

        response = HttpResponse(instance.media, content_type=f'image/{image_type}', status=status.HTTP_200_OK)
        # response['Content-Disvacancy'] = f'attachment; filename="{instance.media_name}"'
        # response['Content-Disvacancy'] = 'inline'

        return response


class HomeView(TemplateView):
    template_name = 'index.html'


class EmployeePageView(TemplateView):
    template_name = 'employee.html'


class Login(APIView):
    def get(self, request):
        return


class Signup(APIView):
    def get(self, request):
        return


class Test(APIView):
    def get(self, request):
        return render(request, 'registration/role-choice.html')


def role_choice_view(request):  # replace with JS
    if request.method == 'GET':
        return render(request, 'registration/role-choice.html')


def login_user(request, password=None):
    if request.user.is_authenticated:
        return

    if request.method == 'POST':  # do I really need to specify post method?
        username = request.POST['username'].lower()
        if password is not None:
            pass
        elif 'password1' in request.POST:
            password = request.POST['password1']
        elif 'password' in request.POST:
            password = request.POST['password']
        else:
            return HttpResponse('Unknown error', status=status.HTTP_400_BAD_REQUEST)

        user = TheUser.objects.filter(username=username).first()
        print(user.check_password(password))  # TODO: False
        # ig the problem is in register view. It saves somehow a wrong password
        if not user:
            print('not user')

        if user and user.check_password(password):
            login(request, user)
            return True
        else:
            return False
            # return Response(f'Username or password is incorrect', status=status.HTTP_400_BAD_REQUEST)


def logout_view(request):
    if request.method == 'GET':
        return render(request, 'registration/logout.html')
    elif request.method == 'POST':
        logout(request)
        return redirect('register')


def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already registered")
        return redirect('home')
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            role = form.instance.role
            form.save()
            logged_in = login_user(request, TheUser.objects.get(username=request.POST['username']).password)
            # return redirect('home')
            if logged_in:
                return redirect(f'register-{role}')
            else:
                messages.error(request, 'shit happened')
                return redirect('register')
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    # return render(request, "registration/register-js.html")
    return render(request, "registration/register.html", {"form": form})


def register_company_view(request):
    if not request.user.is_authenticated:
        return redirect('register')
    if request.user.role == "e":
        messages.error(request, mark_safe("You are already an employee. "
                                          "To create a company you should make "
                                          "<a href='/api/logout/'>register a new account</a>"))
        return redirect('home')
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.data._mutable = True
            form.data.update({'user': request.user.id})
            # form.data.update({'user_id': request.user.id})
            serializer = CompanySerializer(data=form.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return redirect('home')
    else:
        form = CompanyRegistrationForm(initial={'name': request.user.first_name + ' ' + request.user.last_name})
    return render(request, 'company/company-registration.html', {'form': form,
                                                                 'h1': 'New company',
                                                                 'form_action': '/api/register/c/'})


def register_employee_view(request):
    if not request.user.is_authenticated:
        redirect('register')
    if Employee.objects.filter(user=request.user.id).first():
        return HttpResponse('You already registered as an employee', status=status.HTTP_307_TEMPORARY_REDIRECT)
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            form.data._mutable = True
            form.data.update({'user': request.user.id})
            serializer = EmployeeSerializer(data=form.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return redirect('home')
    else:
        form = EmployeeRegistrationForm(initial={'phone': request.user.phone, 'email': request.user.email})
    return render(request, 'employee/employee-registration.html', {'form': form,
                                                                   'h1': 'New employee',
                                                                   'form_action': '/api/register/e/'})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('home')
    if request.method == 'POST':
        logging = login_user(request)
        if logging is True:
            messages.success(request, "You have logged in!")
            return redirect('home')  # TODO: redirect to user page or something
        else:
            messages.error(request, f"Something went wrong: {logging.data}")
            return redirect('login')
    else:
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})


def is_authenticated_shortcut_view(request):  # for development
    if request.user.is_authenticated:
        return HttpResponse(f'User is authenticated, user id - {request.user.id}', status=status.HTTP_200_OK)
    else:
        return HttpResponse("User isn't authenticated", status=status.HTTP_401_UNAUTHORIZED)


def company_choice_view(request, redirect_to: str):
    """
    request - request
    redirect_to - path name of the link where you need a company_id as a kwarg
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please authorise first")
        return redirect('register')
    if not Company.objects.filter(user=request.user.id).first():
        messages.error(request,
                       mark_safe("You don't own a company. "
                                 "If you want to create a company use <a href='/api/register/c/'>this link</a>"))
        return redirect('home')
    companies = Company.objects.filter(user=request.user.id)
    context = {'companies': companies,
               'redirect_to': redirect_to}

    return render(request, 'vacancy/company-choice.html', context)


def company_profile_view(request):
    return company_choice_view(request, 'company-page')


def user_profile(request):
    pass


def vacancies_view(request):
    pass


# def new_vacancy_view(request, **kwargs):
#     if not request.user.is_authenticated:
#         return HttpResponse("You can't use this page, please authorise", status=status.HTTP_401_UNAUTHORIZED)
#     company = Company.objects.get(name=kwargs['company_name'])
#     if company.user != request.user.id:
#         messages.warning(request, "You don't own this company")
#         return redirect('company-choice')


@login_required
def new_vacancy_view(request, **kwargs):
    if not bool(kwargs):
        return company_choice_view(request, 'new-vacancy')
    company = Company.objects.filter(id=kwargs['company_id']).first()
    if not company:
        messages.error(request, 'There is no such a company')
        redirect('home')
    if company.user.id != request.user.id:
        messages.warning(request, "You don't own this company")
        return company_choice_view(request, 'new-vacancy')
    if request.method == 'POST':
        form = NewVacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.owner = company
            vacancy.save()
            vacancy.tags.set(form.cleaned_data['tags'])
            return redirect('home')
    else:
        form = NewVacancyForm()

    return render(request, 'vacancy/create_vacancy.html', {'form': form})


@require_GET
def search_tags(request):
    query = request.GET.get('tag_search', '')
    if query:
        tags = VacancyTag.objects.filter(name__icontains=query)[:10]
        results = [{'id': tag.id, 'name': tag.name} for tag in tags]
    else:
        results = []
    return JsonResponse({'results': results})


def show_vacancy_view(request, **kwargs):
    vacancy = Vacancy.objects.filter(id=kwargs['vacancy_id']).first()
    if not vacancy:
        messages.error(request, 'There is no such a vacancy')
        return redirect('home')
    is_owner = False
    if request.user == vacancy.owner.user:
        is_owner = True
    return render(request, 'vacancy/show-vacancy.html', {'vacancy': vacancy,
                                                         'is_owner': is_owner})


@login_required
def vacancy_edit_view(request, **kwargs):
    vacancy = Vacancy.objects.filter(id=kwargs['vacancy_id']).first()
    if not vacancy:
        messages.error(request, 'There is no such a vacancy')
        return redirect('home')
    if vacancy.owner.user != request.user:
        messages.error(request, 'You can not edit this vacancy')
        return redirect('home')
    if request.method == 'POST':
        form = NewVacancyForm(request.POST)
        if form.is_valid():
            vacancy.tags.set(form.cleaned_data.pop('tags'))
            Vacancy.objects.update_or_create(id=vacancy.id, defaults=form.cleaned_data)
            return redirect('home')
    else:
        initial = dict()
        for field in Vacancy._meta.get_fields()[1:]:
            initial.update({field.name: vacancy.serializable_value(field.name)})
        form = NewVacancyForm(initial=initial)
    return render(request, 'vacancy/create_vacancy.html', {'form': form})


@login_required
def company_edit_view(request, **kwargs):
    company = Company.objects.filter(id=kwargs['company_id']).first()
    if not company:
        messages.error(request, 'There is no such a company')
        return redirect('home')
    if company.user != request.user:
        messages.error(request, 'You can not edit this company')
        return redirect('home')
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            Company.objects.update_or_create(id=company.id, defaults=form.cleaned_data)
            messages.success(request, "Company info was successfully updated!")
            return redirect(f'/api/company/{kwargs["company_id"]}')
    else:
        initial = dict()
        for field in Company._meta.get_fields()[2:]:
            initial.update({field.name: company.serializable_value(field.name)})
        form = EmployeeRegistrationForm(initial=initial)
    return render(request, 'company/company-registration.html', {'form': form,
                                                                 'h1': 'Edit company info',
                                                                 'form_action':
                                                                     f'/api/company/edit/{kwargs["company_id"]}/'})


def company_page_view(request, **kwargs):
    company = Company.objects.filter(id=kwargs['company_id']).first()
    if not company:
        messages.error(request, 'There is no such a company')
        return redirect('home')
    vacancies = Vacancy.objects.filter(owner=company.id)
    is_owner = False
    if request.user == company.user:
        is_owner = True
    return render(request, 'company/company-page.html', {'company': company,
                                                         'vacancies': vacancies,
                                                         'is_owner': is_owner})


def employee_page_view(request, **kwargs):
    employee = Employee.objects.filter(id=kwargs['employee_id']).first()
    if not employee:
        messages.error(request, 'There is no such an employee')
        return redirect('home')
    is_owner = False
    if request.user == employee.user:
        is_owner = True
    return render(request, 'employee/employee-page.html', {'employee': employee,
                                                           'is_owner': is_owner})


@login_required
def employee_edit_view(request, **kwargs):
    employee = Employee.objects.filter(id=kwargs['employee_id']).first()
    if not employee:
        messages.error(request, 'There is no such a profile')
        return redirect('home')
    if employee.user != request.user:
        messages.error(request, 'You can not edit this profile')
        return redirect('home')
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            Employee.objects.update_or_create(id=employee.id, defaults=form.cleaned_data)
            messages.success(request, "Your profile was successfully updated!")
            return redirect(f'/api/employee/{kwargs["employee_id"]}')
    else:
        initial = dict()
        for field in Employee._meta.get_fields():
            initial.update({field.name: employee.serializable_value(field.name)})
        form = EmployeeRegistrationForm(initial=initial)
    return render(request, 'employee/employee-registration.html', {'form': form,
                                                                   'h1': 'Edit employee profile',
                                                                   'form_action':
                                                                       f'/api/employee/edit/{kwargs["employee_id"]}/'})


def test_view(request):  # testing searching algorithm
    if request.method == 'POST':
        response = requests.request(method='get', url='http://127.0.0.1:8000/api/test', params={'colors': ['red', 'green', 'blue']})
        return response
    elif request.method == 'GET':
        params = dict(request.GET)
        print(params['colors'])  # params == {'colors': ['red', 'green', 'blue']}
        return render(request, '/api/test/')
    else:
        return HttpResponse(request)
        # return HttpResponse(request.GET)


def test_slash_view(request):
    return render(request, 'test.html')


def test2(request):  # doesn't work :(
    # but works in other views :/
    # keine Ahnung woran die Sache liegt
    messages.error(request, 'error')
    messages.success(request, 'success')
    messages.info(request, 'info')
    return redirect('home')
