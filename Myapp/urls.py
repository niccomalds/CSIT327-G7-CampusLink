from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('studentDashboard/', views.studentDashboard, name='studentDashboard'),
    path('organizationDashboard/', views.organizationDashboard, name='organization_dashboard'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('create-application/<int:posting_id>/', views.create_application, name='create_application'),
    path('withdraw-application/<int:application_id>/', views.withdraw_application, name='withdraw_application'),
    path('profile/', views.profile_view, name='profile'),
]   