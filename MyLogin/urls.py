from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),

    # Dashboard URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
     path('student/profile/', views.profile, name='profile'),

]






