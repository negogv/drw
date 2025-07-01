import requests
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
import mysql.connector
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import ManyToManyRel, ManyToManyField, ObjectDoesNotExist, query
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.contrib import messages
from requests_toolbelt.multipart.encoder import MultipartEncoder
from django.core.management.base import BaseCommand
from django.utils.safestring import mark_safe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import BaseRenderer
from rest_framework import generics, viewsets, status
from . import serializers
import api.models
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from .forms import RegistrationForm, LoginForm, EmployeeRegistrationForm, CompanyRegistrationForm, NewVacancyForm
import json
from abc import ABC, abstractmethod
import struct

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
        instance = getattr(api.models, model_name).objects \
            .filter(salary__gte=min_salary) \
            .filter(salary__lte=max_salary).filter(salary_type__in=salary_type)


class MultipartRenderer(BaseRenderer):
    media_type = 'multipart/form-data'
    format = 'multipart'

    def render(self, data, media_type=None, renderer_context=None):
        multipart_data = MultipartEncoder(fields=data)
        return multipart_data.to_string()


class GetMediaFileElement(APIView):
    renderer_classes = [MultipartRenderer]

    def get(self, request, **kwargs):
        try:
            media = MediaFile.objects.get(id=kwargs['media_id'])
            return Response({'mediaName': media.name,
                             'mediaBlob': media.binary},
                            content_type='multipart/form-data',
                            status=status.HTTP_200_OK)
        except MediaFile.DoesNotExist:
            return JsonResponse({'error': 'Not Found',
                                 'message': "MediaFile object isn't found"}, status=404)


class GetMediaArrayFromInst(APIView):

    def post(self, request, **kwargs):
        model_name = request.data.get('modelName').capitalize()
        model_id = request.data.get('modelId')
        instance = getattr(api.models, model_name).objects.get(id=model_id)
        all_media = list(instance.media.all())
        body = []
        for media in all_media:
            body.append(media.id)
        return JsonResponse(body, safe=False, status=200)


def create_mediafile(file) -> MediaFile:
    """
    Takes an image in format TemporaryUploadedFile, saves in api_mediafile table and returns new-created primary key
    """
    with transaction.atomic():
        binary_data = b''.join(chunk for chunk in file.chunks())

        media_file = MediaFile.objects.create(
            binary=binary_data,
            name=file.name
        )
    return media_file


class CreateOneMediaFile(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser, FileUploadParser)

    def post(self, request, **kwargs):
        # TODO: read func doc
        """
        rewrite to update endpoint (idk do i even need this at all, I doubt that that's rational. Wouldn't it better
        from optimisation point of view to just delete old and create new element?)(like, yeah, it will change image to
        all instances, but how would one media element be linked to different elements?)

        request body must have a file and name of the model where the media belongs and model id
        """
        file_obj = request.data.get('file')
        if not file_obj:
            return JsonResponse({'error': 'File not provided',
                                 'message': 'Please upload a file'}, status=400)
        model_name = kwargs['model_name'].capitalize()
        model_id = kwargs['model_id']
        instance = getattr(api.models, model_name).objects.filter(id=model_id).first()
        if instance is None:
            return JsonResponse({'error': 'Not Found',
                                 'message': "Instance object isn't found"}, status=404)
        # TODO: set created media as first in manyToMany field
        media_id = create_mediafile(file_obj)
        instance.media.set([media_id])
        instance.save()

        return JsonResponse({'mediaId': media_id.id}, status=200)


class CreateManyMediaFiles(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser, FileUploadParser)

    def post(self, request, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return JsonResponse({'error': 'File not provided',
                                 'message': 'Please upload a file'}, status=400)
        model_name = kwargs['model_name'].capitalize()
        model_id = kwargs['model_id']
        instance = getattr(api.models, model_name).objects.filter(id=model_id).first()
        if instance is None:
            return JsonResponse({'error': 'Not Found',
                                 'message': "Instance object isn't found"}, status=404)

        media_id = create_mediafile(file_obj)
        instance.media.add(media_id)
        instance.save()

        return JsonResponse({'mediaId': media_id.id}, status=200)


class MediaFileRetrieve(APIView):
    def get(self, request, **kwargs):
        """
        Returns a response with an image that was saved in MediaFile with primary key "kwargs['pk']"
        Uncomment first from return or second from return line to display image in browser or download, respectively
        """
        instance = MediaFile.objects.get(id=kwargs['pk'])

        image_type = instance.name.split('.')[-1]

        response = HttpResponse(instance.binary, content_type=f'image/{image_type}', status=status.HTTP_200_OK)
        response['Content-Disvacancy'] = f'attachment; filename="{instance.name}"'
        # response['Content-Disvacancy'] = 'inline'
        return response


class HomeView(TemplateView):
    template_name = 'index.html'


class DeleteInstance(APIView):
    def delete(self, request, **kwargs):
        model_name = kwargs['model_name'].capitalize()
        model_id = kwargs['model_id']
        try:
            instance = getattr(api.models, model_name).objects.get(id=model_id)
            instance.delete()
            return JsonResponse({}, status=204)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Not Found',
                                 'message': "The models wasn't found, change your request"}, status=404)


@require_POST
def update_user_endpoint(request):
    data = json.loads(request.body.decode('utf-8'))
    try:
        obj = TheUser.objects.get(id=data.pop("id"))
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return HttpResponse({}, status=status.HTTP_202_ACCEPTED)
    except TheUser.DoesNotExist:
        return HttpResponse({}, status=status.HTTP_404_NOT_FOUND)


@require_POST
def apply_for_vac_endpoint(request, **kwargs):
    try:
        vacancy = Vacancy.objects.get(id=kwargs['vacancy_id'])
        employee = Employee.objects.get(user=kwargs['user_id'])
        vacancy.respondents.add(employee)
        return HttpResponse({}, status=status.HTTP_202_ACCEPTED)
    except Vacancy.DoesNotExist or Employee.DoesNotExist:
        return HttpResponse({}, status=status.HTTP_404_NOT_FOUND)


@require_POST
def decline_application_endpoint(request, **kwargs):
    try:
        data = json.loads(request.body.decode('utf-8'))
        employee = Employee.objects.get(id=data['respondentId'])
        vacancy = Vacancy.objects.get(id=kwargs['vacancy_id'])
        vacancy.respondents.remove(employee)
        return JsonResponse({}, status=204)
    except Vacancy.DoesNotExist or Employee.DoesNotExist:
        return JsonResponse({'error': 'Not Found',
                             'message': "One or both of the models wasn't found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Bad Request',
                             'message': 'Data in request body is invalid'}, status=400)


@csrf_exempt
@require_POST
def validate_username_endpoint(request):
    data = json.loads(request.body.decode('utf-8'))
    if TheUser.objects.filter(username=data['username']):
        return JsonResponse({'error': 'Not available',
                             'message': 'Username is not available'}, status=409)
    else:
        return JsonResponse({}, status=204)


@require_GET
def get_user_data_endpoint(request, **kwargs):
    try:
        user = TheUser.objects.get(id=kwargs['user_id'])
        return JsonResponse({'username': user.username,
                             'firstName': user.first_name,
                             'lastName': user.last_name,
                             'email': user.email,
                             'phone': user.phone,
                             'role': user.role})
    except TheUser.DoesNotExist:
        return HttpResponse({}, status=status.HTTP_404_NOT_FOUND)


@require_GET
def get_usernames_endpoint(request):
    users = TheUser.objects.all()
    usernames = []
    for user in users:
        usernames.append(user.username)
    return JsonResponse({'usernames': usernames})


@require_GET
def get_vacancy_endpoint(request, **kwargs):
    try:
        vacancy = Vacancy.objects.get(id=kwargs['vacancy_id'])

        body = dict()
        for field in Vacancy._meta.get_fields()[2:]:
            if isinstance(field, ManyToManyField):
                field_values = []
                for el in vacancy.__getattribute__(field.attname).all():
                    field_values.append({'name': el.name,
                                         'id': el.id})
                body.update({field.name: field_values})
            elif field.attname == 'currency_id':
                currency = Currency.objects.get(id=vacancy.serializable_value(field.name))
                body.update({field.name: currency.code})
            else:
                body.update({field.name: vacancy.serializable_value(field.name)})
        return JsonResponse(body)
    except Vacancy.DoesNotExist:
        return JsonResponse({'error': 'Not Found',
                             'message': 'Vacancy instance was not found, change your request'}, status=404)


@require_GET
def get_vac_respondents_endpoint(request, **kwargs):
    try:  # TODO: the func just skips a cv, because there is no corresponding functionality yet
        vacancy = Vacancy.objects.get(id=kwargs['vacancy_id'])
        body = []
        for resp in vacancy.respondents.all():
            resp_dict = model_to_dict(resp)
            resp_dict.pop('cv', None)
            body.append(resp_dict)
        return JsonResponse(body, safe=False, status=200)
    except Vacancy.DoesNotExist:
        return JsonResponse({}, status=404)


@require_GET
def get_vacs_e_profile_endpoint(request, **kwargs):
    employee = Employee.objects.filter(user=kwargs['user_id']).first()
    vacancy = Vacancy.objects.filter(respondents__id=employee.id)
    if employee and vacancy:
        body = []
        for vac in list(vacancy):
            body.append({'title': vac.title,
                         'location': vac.city + ', ' + vac.country,
                         'companyId': vac.owner.id,
                         'companyName': vac.owner.name})
        return JsonResponse(body, safe=False)
    else:
        return HttpResponse('', status=status.HTTP_404_NOT_FOUND)


@require_GET
def get_vacs_c_profile_endpoint(request, **kwargs):
    companies = Company.objects.filter(user__id=kwargs['user_id'])
    if list(companies.all()).__len__() > 0:
        body = []
        for company in list(companies.all()):
            vacancies = Vacancy.objects.filter(owner__id=company.id)
            response_num = 0
            for vac in vacancies:
                response_num += list(vac.respondents.all()).__len__()
            body.append({'companyName': company.name,
                         'companyId': company.id,
                         'vacanciesNum': list(vacancies.all()).__len__(),
                         'responseNum': response_num,
                         'companyLocation': company.city + ", " + company.country})
        return JsonResponse(body, safe=False)
    else:
        return JsonResponse({'error': 'Companies are not found'}, status=204)


@require_GET
def get_company_endpoint(request, **kwargs):
    try:
        company = Company.objects.get(id=kwargs['company_id'])
        company_media = [media.id for media in company.media.all()]
        company_dict = model_to_dict(company, exclude='media')
        company_dict.update({'media': company_media})
        return JsonResponse(company_dict, safe=False)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company is not found'}, status=204)


@require_GET
def get_companies_w_user_endpoint(request, **kwargs):
    companies = Company.objects.filter(user__id=kwargs['user_id'])
    if list(companies.all()).__len__() > 0:
        companies_list = []
        for company in companies:
            companies_list.append(model_to_dict(company))
        return JsonResponse(companies_list, safe=False)
    else:
        return JsonResponse({}, status=204)


@require_GET
def get_all_skills_endpoint(request):
    skills = Skill.objects.all()
    body = []
    for skill in skills:
        body.append({'id': skill.id,
                     'name': skill.name})
    return JsonResponse(body, safe=False)


@require_GET
def get_skills_endpoint(request, **kwargs):
    """
    request.body must be json with list with skill.id's
    """
    data = json.loads(request.body.decode('utf-8'))
    skills = Skill.objects.filter(id__in=data['idList'])
    body = []
    for skill in skills:
        body.append({'id': skill.id,
                     'name': skill.name})
    return JsonResponse(body, safe=False)


def login_user(request, password=None):
    if request.user.is_authenticated:
        return

    if request.method == 'POST':  # do I really need to specify post method?
        username = request.POST['username'].lower()
        if not password:
            password = request.POST.get('password1') or request.POST.get('password')
        if password is None:
            return HttpResponse('Unknown error', status=status.HTTP_400_BAD_REQUEST)

        user = TheUser.objects.filter(username=username).first()

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
            logged_in = login_user(request, request.POST['password1'])
            if logged_in:  # True
                return JsonResponse({'redirectTo': reverse(f'register-{role}')})
            else:
                messages.error(request, 'password is incorrect')
                return JsonResponse({'redirectTo': reverse('register')})
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html")
    # return render(request, "registration/register.html", {"form": form})


@login_required
def register_company_view(request):
    if not request.user.is_authenticated:
        return redirect('register')
    if request.user.role == "employee":
        messages.error(request, mark_safe("You are already an employee. "
                                          "To create a company you should "
                                          "<a href='/api/logout/'>log out</a> and register a new account"))
        return redirect('home')
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.data._mutable = True
            form.data.update({'user': request.user.id})
            serializer = CompanySerializer(data=form.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return redirect('home')
    else:
        form = CompanyRegistrationForm(initial={'name': request.user.first_name + ' ' + request.user.last_name})
    return render(request, 'registration/role-form.html', {'form': form,
                                                           'h1': 'New company',
                                                           'form_action': '/api/company/register/'})


@login_required
def register_employee_view(request):
    if not request.user.is_authenticated:
        redirect('register')
    if request.user.role == 'company':
        messages.error(request, mark_safe("You are already a company(to offer jobs). "
                                          "To create an employee account you should "
                                          "<a href='/api/logout/'>log out</a> and register a new account"))
        return redirect('home')
    if Employee.objects.filter(user=request.user.id).first():
        messages.warning(request, 'You already registered as an employee')
        return redirect(f'/api/employee/{Employee.objects.get(user=request.user.id).id}/')
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = TheUser.objects.get(id=request.user.id)
            employee.save()
            skills_list = [int(id) for id in form.cleaned_data['skills'].split('-')]
            skills = Skill.objects.filter(id__in=skills_list)
            employee.skills.set(skills)
            media_id = int(form.cleaned_data['media'])
            media_instance = MediaFile.objects.filter(id=media_id).first()
            employee.media.add(media_instance)
            return redirect('/api/employee/me/')
        else:
            messages.error(request, form.errors)
    else:
        form = EmployeeRegistrationForm(initial={'phone': request.user.phone, 'email': request.user.email})
    return render(request, 'registration/employee-form.html', {'form': form,
                                                               'h1': 'New employee',
                                                               'form_action': '/api/employee/register/'})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('home')
    if request.method == 'POST':
        logging = login_user(request)
        if logging is True:
            messages.success(request, "You have logged in!")
            return redirect('profile')
        else:
            messages.error(request, f"Password and username aren't passing to each other")
            return redirect('login')
    else:
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})


def is_authenticated_shortcut_view(request):  # for development
    if request.user.is_authenticated:
        return HttpResponse(f'User is authenticated, user id - {request.user.id}', status=status.HTTP_200_OK)
    else:
        return HttpResponse("User isn't authenticated", status=status.HTTP_401_UNAUTHORIZED)


@login_required
def user_profile(request):
    return render(request, 'profile/profile-page.html', {'user_id': request.user.id})


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
                                 "If you want to create a company use <a href='/api/company/register/'>this link</a>"))
        return redirect('home')
    companies = Company.objects.filter(user=request.user.id)
    context = {'companies': companies,
               'redirect_to': redirect_to}

    return render(request, 'vacancy/company-choice.html', context)


def company_profile_view(request):
    return company_choice_view(request, 'company-page')


def vacancies_view(request):
    pass


@login_required
def new_vacancy_view(request, **kwargs):
    if not bool(kwargs):
        return company_choice_view(request, 'new-vacancy')
    company = Company.objects.filter(id=kwargs['company_id']).first()
    if not company:
        messages.error(request, 'There is no such a company')
        return redirect('home')
    if company.user.id != request.user.id:
        messages.warning(request, "You don't own this company")
        return company_choice_view(request, 'new-vacancy')
    if request.method == 'POST':
        form = NewVacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.owner = company
            vacancy.save()
            skills_list = [int(id) for id in form.cleaned_data['tags'].split('-')]
            skills = Skill.objects.filter(id__in=skills_list)
            vacancy.tags.set(skills)
            return redirect('home')
        else:
            messages.error(request, form.errors)
    else:
        form = NewVacancyForm()

    return render(request, 'vacancy/create_vacancy.html', {'form': form})


@require_GET
def search_tags(request):
    query = request.GET.get('tag_search', '')
    # if there is model article with foreign key to r(reporter) you can find all articles where the r is a foreign key
    # r.article_set.all()
    # r.article_set.filter(headline__startswith="This")
    if query:
        tags = Skill.objects.filter(name__icontains=query)[:10]
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
    return render(request, 'vacancy/show-vacancy.html', {'is_owner': is_owner})


@login_required
def vacancy_edit_view(request, **kwargs):
    vacancy = Vacancy.objects.filter(id=kwargs['vacancy_id']).first()
    if not vacancy:
        messages.error(request, 'There is no such a vacancy')
        return redirect('home')
    if vacancy.owner.user != request.user:
        messages.error(request, 'You can not edit this vacancy')
        return redirect('home')
    manyToManyFields = dict()
    if request.method == 'POST':
        form = NewVacancyForm(request.POST)
        if form.is_valid():
            tag_str = form.cleaned_data.pop('tags')
            form.cleaned_data.pop('media')
            Vacancy.objects.update_or_create(id=vacancy.id, defaults=form.cleaned_data)
            if tag_str.__len__() > 0:
                tags = tag_str.split('-')
                vacancy.tags.set(tags)
            return redirect('show-vacancy', vacancy_id=vacancy.id)
        else:
            messages.error(request, form.errors)
    else:
        initial = dict()
        manyToManyFields = dict()
        for field in Vacancy._meta.get_fields()[2:]:
            if isinstance(field, ManyToManyField):
                field_values = []
                for el in vacancy.__getattribute__(field.attname).all():
                    field_values.append({'name': el.name,
                                         'id': el.id})
                manyToManyFields.update({field.name: field_values})
            elif field.attname == 'currency_id':
                currency = Currency.objects.get(id=vacancy.serializable_value(field.name))
                initial.update({field.name: currency.code})
            else:
                initial.update({field.name: vacancy.serializable_value(field.name)})
        form = NewVacancyForm(initial=initial)
    return render(request, 'vacancy/edit-vacancy.html', {'form': form,
                                                         'manyToManyFields': manyToManyFields})


@login_required
def manage_vacancy_view(request, **kwargs):
    vacancy = Vacancy.objects.filter(id=kwargs['vacancy_id']).first()
    if not vacancy:
        messages.error(request, "There is no such a vacancy")
        return redirect("home")
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            vacancy.respondents.remove(Employee.objects.get(id=data['employeeId']))
            return JsonResponse({}, status=204)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found',
                                 'message': 'There is no such an employee'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Empty body',
                                 'message': 'Please, provide an acceptable body'}, status=422)
    elif request.method == 'GET':
        if vacancy.owner.user != request.user:
            messages.error(request, 'You can not access this page')
            return redirect('home')
        return render(request, 'vacancy/manage-vacancy.html', {'vacancyId': kwargs['vacancy_id']})


def search_instances(request: Request, objects: query.QuerySet):
    params = {'state': '',
              'city': ''}
    for key, value in request.POST.dict().items():
        params.update({key: value})
    filtered_inst = objects.filter(
        country__icontains=params['country']).filter(
        state__icontains=params['state']).filter(
        city__icontains=params['city'])
    if 'min-salary' in params and params['min-salary'] != '':
        filtered_inst = filtered_inst.filter(salary__gte=params['min-salary'])
    if 'max-salary' in params and params['max-salary'] != '':
        filtered_inst = filtered_inst.filter(salary__lte=params['max-salary'])
    if 'tags' in params and params['tags'] != '':
        tags = params['tags'].split('-')
        filtered_inst = filtered_inst.filter(tags__in=tags)
    if 'skills' in params and params['skills'] != '':
        tags = params['skills'].split('-')
        filtered_inst = filtered_inst.filter(skills__in=tags)
    filter_text = filtered_inst.filter(text__icontains=params['text_search'])
    try:
        filtered_inst = filtered_inst.filter(title__icontains=params['text_search'])
    except:
        filtered_inst = filtered_inst.filter(name__icontains=params['text_search'])
    filtered_inst = filtered_inst.union(filter_text)
    return filtered_inst


def search_model_view(request: Request, **kwargs):  # TODO: search salary by currency
    model_name = kwargs['model_name'].capitalize()
    if request.method == 'POST':
        objects = getattr(api.models, model_name).objects.all()
        filtered_inst = search_instances(request, objects)

        body = []
        for instance in filtered_inst:
            inst_dict = model_to_dict(instance, exclude=['media', 'respondents', 'tags', 'cv', 'skills'])
            if hasattr(instance, 'tags'):
                inst_dict['owner'] = instance.owner.name
                inst_dict.update({'tags': [tag.name for tag in instance.tags.all()]})
                inst_dict['currency'] = Currency.objects.get(id=inst_dict['currency']).name
            elif hasattr(instance, 'skills'):
                inst_dict.update({'skills': [skill.name for skill in instance.skills.all()]})
            body.append(inst_dict)
        return JsonResponse(body, safe=False, status=200)
    else:
        return render(request, f'search/search-{model_name}.html')


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
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('media')
            Company.objects.update_or_create(id=company.id, defaults=form.cleaned_data)
            messages.success(request, "Company info was successfully updated!")
            return redirect(f'/api/company/{kwargs["company_id"]}')
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        initial = dict()
        for field in Company._meta.get_fields()[2:]:
            if not isinstance(field, ManyToManyField):
                initial.update({field.name: company.serializable_value(field.name)})
        form = CompanyRegistrationForm(initial=initial)
    return render(request, 'registration/role-form.html', {'form': form,
                                                           'model_id': company.id,
                                                           'model_name': 'company',
                                                           'h1': 'Edit company info',
                                                           'form_action':
                                                               f'/api/company/edit/{kwargs["company_id"]}/'})


def company_page_view(request, **kwargs):
    if kwargs['company_id'] == 'me':
        return company_choice_view(request, 'company-page')
    company = Company.objects.filter(id=kwargs['company_id']).first()
    if not company:
        messages.error(request, 'There is no such a company')
        return redirect('home')
    vacancies = Vacancy.objects.filter(owner=company.id)
    is_owner = False
    if request.user == company.user:
        is_owner = True
    return render(request, 'company/company-page.html', {'company': company,
                                                         'model_id': company.id,
                                                         'model_name': 'company',
                                                         'vacancies': vacancies,
                                                         'is_owner': is_owner})


@login_required
def employee_page_view(request, **kwargs):
    if kwargs['employee_id'] == 'me':
        employee = Employee.objects.filter(user_id=request.user.id).first()
    else:
        employee = Employee.objects.filter(id=kwargs['employee_id']).first()
    if not employee:
        return redirect('register-employee')
    is_owner = False
    if request.user == employee.user:
        is_owner = True
    return render(request, 'employee/employee-page.html', {'employee': employee,
                                                           'is_owner': is_owner})


@login_required
def employee_edit_view(request, **kwargs):
    employee = Employee.objects.filter(id=kwargs['employee_id']).first()
    manyToManyFields = 0
    if not employee:
        messages.error(request, 'There is no such a profile')
        return redirect('home')
    if employee.user != request.user:
        messages.error(request, 'You can not edit this profile')
        return redirect('home')
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data.pop('skills')
            media = form.cleaned_data.pop('media')
            Employee.objects.update_or_create(id=employee.id, defaults=form.cleaned_data)
            employee.media.set(media)
            messages.success(request, "Your profile was successfully updated!")
            return redirect(f'/api/employee/{kwargs["employee_id"]}')
    else:
        initial = dict()
        manyToManyFields = dict()
        for field in Employee._meta.get_fields()[2:]:
            if isinstance(field, ManyToManyField):
                field_values = []
                for el in employee.__getattribute__(field.attname).all():
                    field_values.append({'name': el.name,
                                         'id': el.id})
                manyToManyFields.update({field.name: field_values})
            else:
                initial.update({field.name: employee.serializable_value(field.name)})
        form = EmployeeRegistrationForm(initial=initial)

    return render(request, 'registration/role-form.html', {'form': form,
                                                           'model_id': employee.id,
                                                           'model_name': 'employee',
                                                           'h1': "Edit employee page",
                                                           'form_action':
                                                               f'/api/employee/edit/{kwargs["employee_id"]}/',
                                                           'manyToManyFields': manyToManyFields })


def test_view(request):
    pass


def test_slash_view(request):
    form = RegistrationForm()
    return render(request, 'test.html', {'form': form})


def test2(request):
    req: requests.Response = requests.post('http://127.0.0.1:8000/api/post/username/validate/',
                                           json={'username': 'anaskn_skl'})
