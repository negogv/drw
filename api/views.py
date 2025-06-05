from django.shortcuts import render, redirect, get_object_or_404
import mysql.connector
from django.http import HttpResponse
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.views.generic import TemplateView
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
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
from .forms import RegistrationForm, LoginForm
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


class EmployerViews:
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer


class EmployerListCreate(EmployerViews, generics.ListCreateAPIView):
    pass


class EmployerRetrieveUpdateDestroy(EmployerViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class JobseekerViews:
    queryset = Jobseeker.objects.all()
    serializer_class = JobseekerSerializer


class JobseekerListCreate(JobseekerViews, viewsets.ModelViewSet):
    # Just for interest to learn how to create a model in django by hands

    def list(self, request, *args, **kwargs):
        queryset = Jobseeker.objects.all()
        serializer_class = JobseekerSerializer(instance=queryset, many=True)
        return Response(data=serializer_class.data, status=200)

    def create(self, request, *args, **kwargs):
        serializer = JobseekerSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JobseekerRetrieveUpdateDestroy(JobseekerViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class PositionViews:
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class PositionListCreate(PositionViews, generics.ListCreateAPIView):
    pass


class PositionRetrieveUpdateDestroy(PositionViews, generics.RetrieveUpdateDestroyAPIView):
    pass


class PositionListByTags(APIView):
    def get(self, request: Request, **kwargs):
        instance = Position.objects.filter(tags__contains=kwargs['tag'])
        serializer = PositionSerializer(instance, many=True)

        return Response(serializer.data)


class PositionListBySalary(generics.ListAPIView):
    serializer_class = PositionSerializer

    def get_queryset(self):
        minimum = self.request.query_params.get('min-salary', 0)
        maximum = self.request.query_params.get('max-salary', 2147483647)
        return Position.objects.filter(salary__gte=minimum).filter(salary__lte=maximum)


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
    queryset = PositionFeedback.objects.all()
    serializer_class = PositionFeedbackSerializer


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
        # response['Content-Disposition'] = f'attachment; filename="{instance.media_name}"'
        # response['Content-Disposition'] = 'inline'

        return response


class HomeView(TemplateView):
    template_name = 'index.html'


class JobseekerPageView(TemplateView):
    template_name = 'jobseeker.html'


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


def register_view(request, **kwargs):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        role = kwargs['role']
        form.instance.role = role
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@api_view(['POST', 'GET'])
# @renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def login_view(request):
    if request.method == 'POST':
        # form = AuthenticationForm(request.POST)
        user = get_object_or_404(TheUser, username=request.POST['username'])
        if not user.check_password(request.POST['password']):
            return Response("missing user", status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


