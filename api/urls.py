from django.urls import path, include
from . import views
import django.contrib.auth.urls

urlpatterns = [
    path('auth/', views.is_authenticated_shortcut_view),
    # path('get/all-companys', views.get_all_companys),
    # path('<str:model/>', views.ModelListCreate.as_view()),
    path('role/', views.role_choice_view),  # TODO: Should I mb make registration in one url with js??
    path('register/', views.register_view, name='register'),
    path('register/c/', views.register_company_view, name='register-company'),
    path('register/e/', views.register_employee_view, name='register-employee'),
    path('login/', views.login_view, name='login'),

    path('home/', views.HomeView.as_view(), name='home'),
    path('employee-page/', views.EmployeePageView.as_view(), name='employee-page'),

    path('company/', views.CompanyListCreate.as_view()),
    path('company/<int:pk>/', views.CompanyRetrieveUpdateDestroy.as_view()),

    path('employee/', views.EmployeeListCreate.as_view({'get': 'list', 'post': 'create'})),
    path('employee/<int:pk>/', views.EmployeeRetrieveUpdateDestroy.as_view()),

    path('media/<str:model>/<int:pk>', views.MediaFileCreate.as_view()),
    path('media/<int:pk>/', views.MediaFileRetrieve.as_view()),

    path('vacancy/', views.VacancyListCreate.as_view()),
    # path('vacancy/<str:tag>/', views.VacancyListByTags.as_view()),  # TODO: replace with search func
    path('vacancy/search/', views.VacancyListBySalary.as_view()),
    path('vacancy/<int:vacancy_id>/', views.show_vacancy_view, name='show-vacancy'),
    path('vacancy/company-choice/', views.vacancy_company_choice_view, name='company-choice'),
    path('vacancy/new/<int:company_id>/', views.new_vacancy_view, name='new-vacancy'),
    path('search_tags/', views.search_tags, name='search_tags'),

    path('test/', views.test_view, name='test')
    # path('', include('django.contrib.auth.urls')),

]