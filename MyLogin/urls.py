from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication ---
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- Home ---
    path('home/', views.home_view, name='home'),

    # --- Student Pages ---
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/dashboard/profile/', views.profile, name='profile'),
    path('student/dashboard/profile/update/', views.update_profile, name='update_profile'),
    path('my-applications/', views.my_applications, name='my_applications'),

    # --- Organization Pages ---
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('organization/manage-postings/', views.manage_postings, name='manage_postings'),
    path('organization/edit-posting/<int:post_id>/', views.edit_posting, name='edit_posting'),
    path('organization/delete-posting/<int:post_id>/', views.delete_posting, name='delete_posting'),
    path('organization/applicants/', views.applicants_list, name='applicants_list'),
    path('organization/org-profile/', views.org_profile, name='org_profile'),
    path('organization/org-settings/', views.org_settings, name='org_settings'),
    path('organization/post-opportunity/', views.post_opportunity, name='post_opportunity'),

    # --- General Pages ---
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications, name='notifications'),

    # === ADMIN VERIFICATION ROUTES ===
    path('admin/verification/', views.admin_verification_dashboard, name='admin_verification_dashboard'),
    path('admin/verify/<int:profile_id>/', views.admin_verify_organization, name='admin_verify_organization'),
    path('admin/verification/stats/', views.admin_verification_stats, name='admin_verification_stats'),

    # === ADMIN POSTING APPROVAL ROUTES ===
    path('admin/postings/approval/', views.admin_posting_approval, name='admin_posting_approval'),
    path('admin/postings/approve/<int:posting_id>/', views.approve_posting, name='approve_posting'),
    path('admin/postings/reject/<int:posting_id>/', views.reject_posting, name='reject_posting'),
    path('admin/postings/detail/<int:posting_id>/', views.posting_detail_modal, name='posting_detail_modal'),
    path('admin/postings/stats/', views.admin_posting_stats, name='admin_posting_stats'),
]
