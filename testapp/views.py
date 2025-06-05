from django.shortcuts import render
from django.http import HttpResponse
import os

# Create your views here.

# view functions with request -> response
# in other words views are request handlers


def say_hello(request):
    return render(request, 'hello.html', {'name': 'Negogv'})
