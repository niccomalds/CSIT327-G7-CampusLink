from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication ---
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- Main pages ---
    path('home/', views.home_view, name='home'),

    # --- Student pages ---
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/dashboard/profile/', views.profile, name='profile'),
    # REMOVE the duplicate


    path('my-applications/', views.my_applications, name='my_applications'),

    # --- Organization pages ---
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('organization/manage-postings/', views.manage_postings, name='manage_postings'),
    path('organization/edit-posting/<int:post_id>/', views.edit_posting, name='edit_posting'),
    path('organization/delete-posting/<int:post_id>/', views.delete_posting, name='delete_posting'),
    path('organization/applicants/', views.applicants_list, name='applicants_list'),
    path('organization/org-profile/', views.org_profile, name='org_profile'),
    path('organization/org-settings/', views.org_settings, name='org_settings'),
    path('organization/post-opportunity/', views.post_opportunity, name='post_opportunity'),

    # --- Profile Update (FIXED) ---
    path('student/dashboard/profile/update/', views.update_profile, name='update_profile'),

    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications, name='notifications'),


]
