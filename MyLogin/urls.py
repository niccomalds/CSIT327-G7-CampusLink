from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication ---
    path('', views.login_view, name='login'),                # default login page
    path('register/', views.register_view, name='register'), # registration page
    path('logout/', views.logout_view, name='logout'),       # logout page

    # --- Main pages ---
    path('home/', views.home_view, name='home'),

    # --- Student pages ---
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('student/dashboard/profile/', views.profile, name='profile'),
    path('student/dashboard/profile/', views.student_profile_view, name='student_profile'),

    # --- Organization pages ---
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
]
