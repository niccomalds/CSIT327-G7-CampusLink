from django.urls import path
from . import views

urlpatterns = [

    # --- Authentication ---
    path('', views.login_view, name='login'),
    path('admin/', views.admin_redirect, name='admin_redirect'),  # Redirect /admin/ to admin login
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- Home ---
    path('home/', views.home_view, name='home'),

    # --- Student Pages ---
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/dashboard/profile/', views.profile, name='profile'),
    path('student/dashboard/profile/update/', views.update_profile, name='update_profile'),
    path('student/dashboard/profile/save-skills/', views.save_skills, name='save_skills'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('create-application/<int:posting_id>/', views.create_application, name='create_application'),

    # --- Organization Pages ---
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('organization/manage-postings/', views.manage_postings, name='manage_postings'),
    path('organization/edit-posting/<int:post_id>/', views.edit_posting, name='edit_posting'),
    path('organization/delete-posting/<int:post_id>/', views.delete_posting, name='delete_posting'),
    path('organization/applicants/', views.applicants_list, name='applicants_list'),
    path('get-application-details/<int:application_id>/', views.get_application_details, name='get_application_details'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),

    # --- ORG PROFILE WIZARD ---
    path('organization/org-profile/', views.org_profile, name='org_profile'),
    path('organization/org-profile/save/', views.save_org_profile, name='save_org_profile'),

    # --- Post Opportunity ---
    path('organization/post-opportunity/', views.post_opportunity, name='post_opportunity'),

    # --- Settings & Notifications ---
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('student/notifications/', views.student_notification, name='student_notification'),


    # 🔔 Notification actions
    path(
        'notifications/<int:pk>/favorite/',
        views.notification_toggle_favorite,
        name='notification_toggle_favorite'
    ),
    path(
        'notifications/<int:pk>/archive/',
        views.notification_archive,
        name='notification_archive'
    ),
    path(
        'notifications/<int:pk>/delete/',
        views.notification_delete,
        name='notification_delete'
    ),
    path(
        'notifications/mark-all-read/',
        views.notification_mark_all_read,
        name='notification_mark_all_read'
    ),

    # === ORGANIZATION VERIFICATION SUBMISSION ===
    path('organization/verify/', views.submit_verification, name='submit_verification'),

    # === ADMIN DASHBOARD ===
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # === ADMIN POSTING APPROVAL ===
    path('admin/postings/approval/', views.admin_posting_approval, name='admin_posting_approval'),
    path('admin/postings/<int:posting_id>/approve/', views.approve_posting, name='approve_posting'),
    path('admin/postings/<int:posting_id>/reject/', views.reject_posting, name='reject_posting'),
    
    # === ADMIN ORGANIZATION VERIFICATION ===
    path('admin/verification/', views.admin_verification_dashboard, name='admin_verification_dashboard'),
    path('admin/verification/<int:profile_id>/approve/', views.approve_organization, name='approve_organization'),
    path('admin/verification/<int:profile_id>/reject/', views.reject_organization, name='reject_organization'),

    path("organization/settings/", views.org_settings, name="org_settings"),
]
