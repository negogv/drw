from django.shortcuts import render, redirect, get_object_or_404
import mysql.connector
from django.http import HttpResponse
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.views.generic import TemplateView
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
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
from .forms import RegistrationForm, LoginForm, EmployeeRegistrationForm, CompanyRegistrationForm
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
        min_salary = request.query_params.get('min-salary', 0)
        max_salary = request.query_params.get('max-salary', 2147483647)
        name = request.query_params.get('name', 2147483647)

        model_name = kwargs['model'].capitalize()
        instance = getattr(api.models, model_name).objects\
            .filter(salary__gte=min_salary)\
            .filter(salary__lte=max_salary)




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


def role_choice_view(request):
    if request.method == 'GET':
        return render(request, 'registration/role-choice.html')


def login_user(request):
    if request.user.is_authenticated:
        return

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password1'] or request.POST['password']

        user = User.objects.filter(username=username).first()

        if user is not None:
            login(request, user)
            return True
        else:
            return Response('Username or password is incorrect', status=status.HTTP_400_BAD_REQUEST)


def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already registered")
        return redirect('home')
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            role = form.instance.role
            form.save()
            login_user(request)
            # return redirect('home')
            return redirect(f'{role}/')
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def register_company_view(request):
    if not request.user.is_authenticated:
        redirect('register')
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
    return render(request, 'registration/company-registration.html', {'form': form})


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
    return render(request, 'registration/employee-registration.html', {'form': form})


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
            messages.error(request, f"Something went wrong\n{logging.data}")
            return redirect('login')
    else:
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})


def is_authenticated_shortcut_view(request):  # for development
    if request.user.is_authenticated:
        return HttpResponse(f'User is authenticated, user id - {request.user.id}', status=status.HTTP_200_OK)
    else:
        return HttpResponse("User isn't authenticated", status=status.HTTP_401_UNAUTHORIZED)


def vacancy_company_choice_view(request):
    if not request.user.is_authenticated:
        return HttpResponse("You can't make a vacancy, please authorise", status=status.HTTP_401_UNAUTHORIZED)
    if not Company.objects.filter(user=request.user.id).first():
        return HttpResponse("You aren't an company, you can't make a vacancy", status=status.HTTP_401_UNAUTHORIZED)
    companies = Company.objects.filter(user=request.user.id)
    context = {'companies': companies}

    return render(request, 'vacancy/company-choice.html', context)


def new_vacancy_view(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponse("You can't use this page, please authorise", status=status.HTTP_401_UNAUTHORIZED)
    company = Company.objects.get(name=kwargs['company_name'])
    if company.user != request.user.id:
        messages.warning(request, "You don't own this company")
        return redirect('company-choice')




def test_view(request):
    messages.error(request, 'bla bla bla')
    return redirect('home')
