from django.urls import path
from . import views

urlpatterns = [
    path('new/employer', views.new_employer),
    path('get/all-employers', views.get_all_employers)
]