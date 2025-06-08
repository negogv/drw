from rest_framework import serializers
from .models import *


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id',
                  'user',
                  'name',
                  'country',
                  'city',
                  'text',
                  'media_array',
                  'created']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id',
                  'user',
                  'country',
                  'city',
                  'phone',
                  'email',
                  'text',
                  'media_array',
                  'cv',
                  'created']


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['id',
                  'owner',
                  'text',
                  'salary',
                  'currency',
                  'salary_type',
                  'media_array',
                  'tags',
                  'created']


class VacancyFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyFeedback
        fields = ['id',
                  'owner',
                  'vacancy',
                  'feedback_type',
                  'file',
                  'text',
                  'created']


class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ['id',
                  'media',
                  'media_name']


class TheUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheUser
        fields = '__all__'
