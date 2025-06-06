from rest_framework import serializers
from .models import *


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
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


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id',
                  'owner',
                  'text',
                  'salary',
                  'salary_type',
                  'media_array',
                  'tags',
                  'created']


class PositionFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionFeedback
        fields = ['id',
                  'owner',
                  'position',
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


class TestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestImage
        fields = ['id',
                  'image']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheUser
        fields = '__all__'
