from django.urls import path, include
from . import views
import django.contrib.auth.urls

urlpatterns = [
    # path('get/all-employers', views.get_all_employers),
    # path('<str:model/>', views.ModelListCreate.as_view()),
    path('role/', views.role_choice_view),  # TODO: Should I mb make registration in one url with js??
    path('register/', views.register_view, name='register'),
    path('register/employer/', views.register_employer_view, name='register-employer'),
    path('register/employee/', views.register_employee_view, name='register-employee'),
    path('login/', views.login_view, name='login'),

    path('home/', views.HomeView.as_view(), name='home'),
    path('employee-page/', views.EmployeePageView.as_view(), name='employee-page'),

    path('employer/', views.EmployerListCreate.as_view()),
    path('employer/<int:pk>/', views.EmployerRetrieveUpdateDestroy.as_view()),

    path('employee/', views.EmployeeListCreate.as_view({'get': 'list', 'post': 'create'})),
    path('employee/<int:pk>/', views.EmployeeRetrieveUpdateDestroy.as_view()),

    path('media/<str:model>/<int:pk>', views.MediaFileCreate.as_view()),
    path('media/<int:pk>/', views.MediaFileRetrieve.as_view()),

    path('position/', views.PositionListCreate.as_view()),
    path('position/<int:pk>/', views.PositionRetrieveUpdateDestroy.as_view()),
    path('position/<str:tag>/', views.PositionListByTags.as_view()),
    path('position/search/', views.PositionListBySalary.as_view()),
    # path('', include('django.contrib.auth.urls')),

]