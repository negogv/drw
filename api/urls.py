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
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),  # user info and link to employee page
                                                           # cuz I don't want to call db from navbar to get employee id

    path('home/', views.HomeView.as_view(), name='home'),

    path('company/', views.CompanyListCreate.as_view()),
    path('company/<int:company_id>/', views.company_page_view, name='company-page'),
    path('company/edit/<int:company_id>/', views.company_edit_view, name='edit-company'),
    path('company/profile/', views.company_profile_view, name='company-profile'),

    path('employee/', views.EmployeeListCreate.as_view({'get': 'list', 'post': 'create'})),
    path('employee/<int:employee_id>/', views.employee_page_view, name='employee-page'),
    path('employee/edit/<int:employee_id>/', views.employee_edit_view, name='edit-employee'),

    path('media/<str:model>/<int:pk>', views.MediaFileCreate.as_view()),
    path('media/<int:pk>/', views.MediaFileRetrieve.as_view()),

    path('vacancy/', views.VacancyListCreate.as_view()),
    # path('vacancy/<str:tag>/', views.VacancyListByTags.as_view()),  # TODO: replace with search func
    # TODO: change vacancy endpoint
    path('vacancies/', views.vacancies_view, name='all-vacancies'),
    path('vacancy/edit/<int:vacancy_id>/', views.vacancy_edit_view, name='edit-vacancy'),
    path('vacancy/search/', views.VacancyListBySalary.as_view()),
    path('vacancy/<int:vacancy_id>/', views.show_vacancy_view, name='show-vacancy'),
    path('vacancy/new/', views.new_vacancy_view, name='vacancy-company-choice'),
    path('vacancy/new/<int:company_id>/', views.new_vacancy_view, name='new-vacancy'),
    path('search_tags/', views.search_tags, name='search_tags'),

    path('test/', views.test_slash_view, name='test-slash'),
    path('test', views.test_view, name='test'),
    path('test2/', views.test2, name='test2'),
    # path('', include('django.contrib.auth.urls')),

]