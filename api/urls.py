from django.urls import path, include
from . import views
import django.contrib.auth.urls

urlpatterns = [
    path('auth/', views.is_authenticated_shortcut_view),
    # endpoints for specific views
    path('get/profile/vacancies/employee/<int:user_id>/', views.get_vacs_e_profile_endpoint),
    path('get/profile/vacancies/company/<int:user_id>/', views.get_vacs_c_profile_endpoint),
    # get endpoints
    path('get/usernames/', views.get_usernames_endpoint),
    path('get/user/data/<int:user_id>/', views.get_user_data_endpoint),
    path('get/company/<int:company_id>/', views.get_company_endpoint),
    path('get/company/list/w-user-id/<int:user_id>/', views.get_companies_w_user_endpoint),
    path('get/vacancy/<int:vacancy_id>/', views.get_vacancy_endpoint),
    path('get/vacancy/<int:vacancy_id>/respondents/', views.get_vac_respondents_endpoint),
    path('get/skills/', views.get_skills_endpoint),
    path('get/skills/all/', views.get_all_skills_endpoint),
    # post endpoints
    path('post/user/', views.update_user_endpoint),
    path('post/vacancy/apply/<int:vacancy_id>/<int:user_id>/', views.apply_for_vac_endpoint),

    path('role/', views.role_choice_view),  # TODO: Should I mb make registration in one url with js??
    path('register/', views.register_view, name='register'),

    path('register/c/', views.register_company_view, name='register-company'),
    path('register/e/', views.register_employee_view, name='register-employee'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),  # user info and link to employee page
                                                           # cuz I don't want to call db from navbar to get employee id

    path('home/', views.HomeView.as_view(), name='home'),

    # TODO: would be better to change urls to pattern "object/object_id/action/" instead of "object/action/object_id/
    path('company/', views.CompanyListCreate.as_view()),
    path('company/<company_id>/', views.company_page_view, name='company-page'),
    path('company/edit/<int:company_id>/', views.company_edit_view, name='edit-company'),
    path('company/profile/', views.company_profile_view, name='company-profile'),

    path('employee/', views.EmployeeListCreate.as_view({'get': 'list', 'post': 'create'})),
    path('employee/<employee_id>/', views.employee_page_view, name='employee-page'),
    path('employee/edit/<int:employee_id>/', views.employee_edit_view, name='edit-employee'),

    path('media/<str:model>/<int:pk>', views.MediaFileCreate.as_view()),
    path('media/<int:pk>/', views.MediaFileRetrieve.as_view()),

    # path('vacancy/', views.VacancyListCreate.as_view()),
    # path('vacancy/<str:tag>/', views.VacancyListByTags.as_view()),
    path('vacancies/', views.vacancies_view, name='all-vacancies'),
    path('vacancy/edit/<int:vacancy_id>/', views.vacancy_edit_view, name='edit-vacancy'),
    path('vacancy/<int:vacancy_id>/manage/', views.manage_vacancy_view, name='manage-vacancy'),
    path('vacancy/search/', views.VacancyListBySalary.as_view()),
    path('vacancy/<int:vacancy_id>/', views.show_vacancy_view, name='show-vacancy'),
    path('vacancy/new/', views.new_vacancy_view, name='vacancy-company-choice'),
    path('vacancy/new/<int:company_id>/', views.new_vacancy_view, name='new-vacancy'),
    path('search_tags/', views.search_tags, name='search_tags'),

    path('test-search/', views.test_view, name='test-search'),
    path('test/', views.get_vacancy_endpoint, name='test'),
    path('test2/', views.test2, name='test2'),
    # path('', include('django.contrib.auth.urls')),

]