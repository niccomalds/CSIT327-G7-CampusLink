from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, login as auth_login
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from Myapp.models import Posting
from .models import Profile, Notification
from Myapp.utils import can_user_apply
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


# --- Session timeout (10 minutes AFK limit) ---
SESSION_TIMEOUT = 600  # seconds


# --- Role-based access decorator ---
def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "You must log in first.")
                return redirect('login')

            # Allow superusers to access any role-restricted view
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if hasattr(request.user, 'profile') and request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "Access denied.")
            return redirect('home')
        return wrapper
    return decorator


# --- Authentication Views ---
def login_view(request):
    if request.method == 'GET' and 'session_expired' in request.GET:
        messages.warning(request, "You were logged out due to inactivity.")

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')  # role from login form

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if hasattr(user, 'profile') and user.profile.role != selected_role:
                messages.error(request, "Access denied. Wrong role selected.")
                return redirect('login')

            login(request, user)
            request.session['last_activity'] = timezone.now().isoformat()

            # Redirect based on role
            if hasattr(user, 'profile'):
                role = user.profile.role
                if role == "Student":
                    return redirect('student_dashboard')
                elif role == "Organization":
                    return redirect('organization_dashboard')
                elif role == "Admin":
                    return redirect('admin_dashboard')

            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def admin_redirect(request):
    """Redirect /admin/ to admin login page"""
    return redirect('admin_login')


# --- Admin Login View ---
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            # Redirect to admin dashboard
            print(f"User {user.username} authenticated and is staff: {user.is_staff}")
            return redirect('admin_dashboard')
        elif user is not None:
            print(f"User {user.username} authenticated but is not staff: {user.is_staff}")
            messages.error(request, "Insufficient permissions. Admin access required.")
        else:
            print("Authentication failed")
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'admin_login.html')


# --- Registration View ---
def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        org_name = request.POST.get('org_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name if role == "Student" else "",
            last_name=last_name if role == "Student" else ""
        )

        # Create profile
        if role == "Organization":
            Profile.objects.create(user=user, role=role, org_name=org_name, institutional_email=email)
        else:
            Profile.objects.create(user=user, role=role)

        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


# --- Home ---
def home_view(request):
    return render(request, 'home.html')


# --- Dashboards ---
@login_required
@role_required(allowed_roles=['Student'])
def student_dashboard(request):
    last_activity = request.session.get('last_activity')
    now = timezone.now()

    if last_activity:
        last_activity = datetime.fromisoformat(last_activity)
        elapsed = (now - last_activity).total_seconds()
        if elapsed > SESSION_TIMEOUT:
            logout(request)
            messages.warning(request, "You were logged out due to inactivity.")
            return redirect(f"{reverse('login')}?session_expired=1")

    request.session['last_activity'] = now.isoformat()
    
    # Get approved postings from verified organizations
    postings = Posting.objects.filter(
        approval_status='approved',
        organization__profile__role='Organization',
        organization__profile__verification_status='verified'
    ).select_related('organization', 'organization__profile').order_by('-created_at')
    
    # Process tags for each posting (convert comma-separated string to list)
    postings_list = []
    for posting in postings:
        tags_list = [tag.strip() for tag in posting.tags.split(',') if tag.strip()] if posting.tags else []
        postings_list.append({
            'posting': posting,
            'tags_list': tags_list,
        })

    # 🔢 DASHBOARD STATS
    today = timezone.now().date()

    # Active opportunities = approved + verified orgs + Active status + deadline in future
    active_opportunities_count = postings.filter(
        status='Active',
        deadline__gte=today
    ).count()

    # Students connected = number of student profiles
    students_connected_count = Profile.objects.filter(role='Student').count()
    
    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    # Get recent notifications for the dropdown (limit to 5 most recent)
    recent_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-timestamp')[:5]
    
    context = {
        'postings_list': postings_list,
        'unread_count': unread_count,
        'notifications': recent_notifications,

        'active_opportunities_count': active_opportunities_count,
        'students_connected_count': students_connected_count,
    }
    
    return render(request, 'student_dashboard.html', context)




@login_required
@role_required(allowed_roles=['Organization'])
def organization_dashboard(request):
    """Organization dashboard with verification status"""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('login')
    
    # Only organizations can access this dashboard
    if profile.role != 'Organization':
        messages.error(request, "Access denied. Organization account required.")
        return redirect('student_dashboard')
    
    # Get organization's postings
    postings = Posting.objects.filter(organization=request.user).order_by('-created_at')
    
    # Example stats (expand as needed)
    active_postings_count = postings.filter(deadline__gte=date.today(), status='Active').count()
    total_applicants = 0
    total_views = 0
    acceptance_rate = 0

    # Verification status context
    verification_context = {
        'is_verified': profile.is_verified_organization(),
        'verification_status': profile.verification_status,
        'needs_verification': profile.role == 'Organization' and profile.verification_status in ['unverified', 'rejected'],
        'is_pending': profile.verification_status == 'pending',
        'show_verified_modal': profile.is_verified_organization() and not request.session.get('verified_modal_shown', False)
    }
    
    # Mark the verified modal as shown if the user is verified
    if profile.is_verified_organization() and not request.session.get('verified_modal_shown', False):
        request.session['verified_modal_shown'] = True
    
    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    # Get recent notifications for the dropdown (limit to 5 most recent)
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
    
    context = {
        'profile': profile,
        'postings': postings,
        'active_postings_count': active_postings_count,
        'total_applicants': total_applicants,
        'total_views': total_views,
        'acceptance_rate': acceptance_rate,
        'recent_postings': postings.filter(approval_status='approved').order_by('-id')[:3],  # Only show approved postings in recent postings
        'today': date.today(),
        'unread_count': unread_count,
        'notifications': recent_notifications,
        **verification_context
    }
    return render(request, 'org_dashboard.html', context)


@login_required
@role_required(allowed_roles=['Admin'])
def admin_dashboard(request):
    """Admin dashboard with platform statistics"""
    # Get pending postings count
    pending_postings_count = Posting.objects.filter(approval_status='pending').count()
    
    # Get pending verifications count
    pending_verifications_count = Profile.objects.filter(
        role='Organization',
        verification_status='pending'
    ).count()
    
    # Get verified organizations
    verified_organizations = Profile.objects.filter(
        role='Organization',
        verification_status='verified'
    ).select_related('user').order_by('-verified_at')
    
    from datetime import date
    context = {
        'total_users': 1248,
        'active_postings': 142,
        'applications_submitted': 856,
        'success_rate': 78,
        'server_status': 'Operational',
        'database_status': 'Connected',
        'error_rate': 'Low (0.2%)',
        'today': date.today(),
        'pending_postings_count': pending_postings_count,
        'pending_verifications_count': pending_verifications_count,
        'verified_organizations': verified_organizations,
    }
    return render(request, 'admin_dashboard.html', context)


# --- Admin Posting Approval Views ---
@login_required
@role_required(allowed_roles=['Admin'])
def admin_posting_approval(request):
    """Display pending postings for admin approval"""
    pending_postings = Posting.objects.filter(approval_status='pending').select_related('organization', 'organization__profile').order_by('-created_at')
    
    context = {
        'pending_postings': pending_postings,
    }
    return render(request, 'admin_posting_approval.html', context)


@login_required
@role_required(allowed_roles=['Admin'])
def approve_posting(request, posting_id):
    """Approve a pending posting"""
    if request.method == 'POST':
        try:
            posting = Posting.objects.select_related('organization').get(
                id=posting_id,
                approval_status='pending'
            )
            posting.approval_status = 'approved'
            posting.approved_at = timezone.now()
            posting.approved_by = request.user
            posting.save()

            # Send notification to the organization
            Notification.objects.create(
                recipient=posting.organization,
                sender=request.user,
                notification_type='posting_approved',
                title=f'Posting Approved: {posting.title}',
                message=f'Your posting "{posting.title}" has been approved by the admin and is now live for students to view.',
                related_posting=posting,
            )

            messages.success(request, f'Posting "{posting.title}" has been approved.')
        except Posting.DoesNotExist:
            messages.error(request, 'Posting not found or already processed.')
        
        return redirect('admin_posting_approval')
    
    return redirect('admin_posting_approval')



@login_required
@role_required(allowed_roles=['Admin'])
def reject_posting(request, posting_id):
    """Reject a pending posting"""
    if request.method == 'POST':
        try:
            posting = Posting.objects.select_related('organization').get(id=posting_id, approval_status='pending')
            rejection_reason = request.POST.get('rejection_reason', '')
            
            posting.approval_status = 'rejected'
            posting.rejection_reason = rejection_reason
            posting.approved_at = timezone.now()
            posting.approved_by = request.user
            posting.save()
            
            messages.success(request, f'Posting "{posting.title}" has been rejected.')
        except Posting.DoesNotExist:
            messages.error(request, 'Posting not found or already processed.')
        
        return redirect('admin_posting_approval')
    
    return redirect('admin_posting_approval')


# --- Profile ---
@login_required
def profile(request):
    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    # Get recent notifications for the dropdown (limit to 5 most recent)
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
    
    return render(request, 'profile.html', {
        "profile": request.user.profile,
        'unread_count': unread_count,
        'notifications': recent_notifications,
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile

        # Update user email (since students should update their main email)
        email = request.POST.get('email')
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()
        
        profile.full_name = request.POST.get('full_name', profile.full_name)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.academic_year = request.POST.get('academic_year', profile.academic_year)
        profile.major = request.POST.get('major', profile.major)
        profile.bio = request.POST.get('bio', profile.bio)

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return redirect('profile')


# --- Organization / Posting Management ---
@login_required
def manage_postings(request):
    if not hasattr(request.user, 'profile'):
        messages.error(request, "Access denied.")
        return redirect('home')

    if request.user.profile.role == "Organization":
        postings = Posting.objects.filter(organization=request.user)
    elif request.user.profile.role == "Admin":
        postings = Posting.objects.all()
    else:
        messages.error(request, "Access denied.")
        return redirect('home')

    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    # Get recent notifications for the dropdown (limit to 5 most recent)
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]

    return render(request, 'manage_posting.html', {
        'postings': postings,
        'unread_count': unread_count,
        'notifications': recent_notifications,
    })


@login_required
def edit_posting(request, post_id):
    try:
        posting = Posting.objects.get(id=post_id)
    except Posting.DoesNotExist:
        messages.error(request, "Posting not found.")
        return redirect('manage_postings')

    if request.user.profile.role == "Organization" and posting.organization != request.user:
        messages.error(request, "Access denied.")
        return redirect('manage_postings')

    if request.method == 'POST':
        posting.title = request.POST.get('title', posting.title)
        posting.description = request.POST.get('description', posting.description)
        posting.deadline = request.POST.get('deadline', posting.deadline)
        posting.status = request.POST.get('status', posting.status)
        posting.save()
        messages.success(request, "Posting updated successfully.")
        return redirect('manage_postings')

    return render(request, 'edit_posting.html', {'posting': posting})


@login_required
def delete_posting(request, post_id):
    try:
        posting = Posting.objects.get(id=post_id)
    except Posting.DoesNotExist:
        messages.error(request, "Posting not found.")
        return redirect('manage_postings')

    if request.user.profile.role == "Organization" and posting.organization != request.user:
        messages.error(request, "Access denied.")
        return redirect('manage_postings')

    if request.method == 'POST':
        posting.delete()
        messages.success(request, "Posting deleted successfully.")
        return redirect('manage_postings')

    return redirect('manage_postings')


# --- Student Applications ---
@login_required
@role_required(allowed_roles=['Student'])
def my_applications(request):
    applications = []
    
    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    # Get recent notifications for the dropdown (limit to 5 most recent)
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
    
    return render(request, 'my_applications.html', {
        'applications': applications,
        'unread_count': unread_count,
        'notifications': recent_notifications,
    })


# --- Organization Applicants ---
@login_required
def applicants_list(request):
    return render(request, 'applicants_list.html')




# --- Organization Profile & Settings ---
@login_required
def org_settings(request):
    return render(request, 'org_settings.html')


# --- Settings & Notifications ---
@login_required
def settings_view(request):
    return render(request, 'settings.html')


# --- Application Status Check (JSON) ---
def check_application_status(request, posting_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'has_applied': False,
            'can_apply': False,
            'message': 'Please log in to apply',
            'status': None
        })

    can_apply, application, message = can_user_apply(request.user, posting_id)

    return JsonResponse({
        'has_applied': not can_apply,
        'can_apply': can_apply,
        'message': message,
        'status': application.status if application else None,
        'application_id': application.id if application else None
    })


# === ORGANIZATION VERIFICATION SUBMISSION ===
@login_required
@role_required(allowed_roles=['Organization'])
def submit_verification(request):
    """Handle organization verification submission"""
    profile = request.user.profile
    
    if profile.verification_status == 'verified':
        messages.info(request, "Your organization is already verified.")
        return redirect('organization_dashboard')
    
    if profile.verification_status == 'pending':
        messages.info(request, "Your verification request is already pending review.")
        return redirect('organization_dashboard')
    
    if request.method == 'POST':
        verification_document = None
        if 'verification_document' in request.FILES:
            verification_document = request.FILES['verification_document']
            
            allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
            if verification_document.content_type not in allowed_types:
                messages.error(request, "Invalid file type. Please upload PDF, PNG, or JPG files only.")
                return render(request, 'org_verification_form.html', {'profile': profile})
            
            if verification_document.size > 5 * 1024 * 1024:
                messages.error(request, "File too large. Maximum file size is 5MB.")
                return render(request, 'org_verification_form.html', {'profile': profile})
        
        if verification_document:
            profile.verification_documents = verification_document
        
        profile.verification_status = 'pending'
        profile.verification_submitted_at = timezone.now()
        profile.save()
        
        messages.success(request, "Verification request submitted successfully! Our team will review your request within 1-2 business days.")
        return redirect('organization_dashboard')
    
    return render(request, 'org_verification_form.html', {'profile': profile})


@login_required
@role_required(allowed_roles=['Organization'])
def post_opportunity(request):
    profile = request.user.profile
    is_verified = profile.is_verified_organization()
    
    if not is_verified:
        messages.error(request, "Only verified organizations can post opportunities. Please verify your organization first.")
        return redirect('submit_verification')

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline_str = request.POST.get('deadline')
        opportunity_type = request.POST.get('opportunity_type')

        selected_tags = request.POST.getlist("tags")
        tags_str = ",".join(selected_tags)

        if not (title and description and deadline_str and opportunity_type):
            messages.error(request, "Please fill in all required fields.")
            return redirect('post_opportunity')

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('post_opportunity')

        if deadline <= timezone.now().date():
            messages.error(request, "Deadline must be in the future.")
            return redirect('post_opportunity')

        approval_status = 'pending'
        
        posting = Posting.objects.create(
            organization=request.user,
            title=title,
            description=description,
            deadline=deadline,
            tags=tags_str,
            approval_status=approval_status,
            opportunity_type=opportunity_type
        )

        success_message = "Opportunity created successfully! Waiting for admin approval."
        messages.success(request, success_message)
        return redirect('organization_dashboard')

    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]

    return render(request, 'post_opportunity.html', {
        'unread_count': unread_count,
        'notifications': recent_notifications,
    })


@login_required
def org_profile(request):
    """Load the single-page organization profile UI."""
    profile = request.user.profile  
    
    # Get unread notification count for the user (ignore archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()
    
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:5]

    context = {
        "user": request.user,
        "profile": profile,
        'unread_count': unread_count,
        'notifications': recent_notifications,
    }
    return render(request, "org_profile.html", context)


@login_required
def save_org_profile(request):
    """Optimized AJAX endpoint for updating the organization profile securely."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    print("Received POST data:", request.POST)
    print("Received FILES:", request.FILES)

    profile = request.user.profile
    errors = {}

    def get_clean(field):
        return request.POST.get(field, "").strip()

    import re
    url_regex = re.compile(r'^(https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*|[a-zA-Z0-9._-]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def valid_url(value):
        return value == "" or url_regex.match(value)

    def valid_email(value):
        return value == "" or email_regex.match(value)

    profile.org_name = get_clean("org_name") or profile.org_name
    profile.description = get_clean("description") or profile.description
    profile.mission = get_clean("mission") or profile.mission
    profile.department = get_clean("department") or profile.department
    profile.website = get_clean("website") or profile.website
    profile.address = get_clean("address") or profile.address

    profile.contact_email = get_clean("contact_email") or profile.contact_email
    profile.contact_phone = get_clean("contact_phone") or profile.contact_phone

    profile.social_facebook = get_clean("social_facebook") or profile.social_facebook
    profile.social_instagram = get_clean("social_instagram") or profile.social_instagram
    profile.social_linkedin = get_clean("social_linkedin") or profile.social_linkedin

    profile.is_public = (request.POST.get("is_public") == "True")

    if not request.POST.get("org_name", "").strip():
        errors["org_name"] = "Organization name is required."

    contact_email = request.POST.get("contact_email", "").strip()
    if contact_email and not valid_email(contact_email):
        errors["contact_email"] = "Invalid email format. Please enter a valid email address."

    contact_phone = request.POST.get("contact_phone", "").strip()
    if contact_phone:
        philippine_phone_pattern = r'^(09|\+639|639)\d{9}$'
        if not re.match(philippine_phone_pattern, contact_phone):
            errors["contact_phone"] = "Please enter a valid Philippine mobile number (e.g., 09123456789 or +639123456789)"

    website = request.POST.get("website", "").strip()
    if website and not valid_url(website):
        errors["website"] = "Invalid website URL. Please enter a full URL (e.g., https://www.yourwebsite.com) or just your domain (e.g., yourwebsite.com)."

    social_links = {
        "facebook": request.POST.get("social_facebook", "").strip(),
        "instagram": request.POST.get("social_instagram", "").strip(),
        "linkedin": request.POST.get("social_linkedin", "").strip(),
    }
    for key, val in social_links.items():
        if val and not valid_url(val):
            errors[f"social_{key}"] = f"Invalid {key.capitalize()} URL. Please enter a valid URL (e.g., https://facebook.com/yourpage) or just your username (e.g., yourpage)."

    if "org_logo" in request.FILES:
        logo = request.FILES["org_logo"]

        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if logo.content_type not in allowed_types:
            errors["org_logo"] = "Invalid file type. Please upload PNG, JPG, or WebP."

        if logo.size > 3 * 1024 * 1024:
            errors["org_logo"] = "File too large. Max file size is 3MB."

        if "org_logo" not in errors:
            profile.org_logo = logo

    if errors:
        print("Validation errors:", errors)
        return JsonResponse({"success": False, "errors": errors}, status=400)

    try:
        if "org_logo" in request.FILES:
            profile.profile_picture = profile.org_logo
        
        profile.save()
        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully!",
            "updated": {
                "org_name": profile.org_name,
                "logo_url": profile.org_logo.url if profile.org_logo else None,
                "profile_picture_url": profile.profile_picture.url if profile.profile_picture else None,
                "is_public": profile.is_public,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# === ADMIN ORGANIZATION VERIFICATION ===
@login_required
@role_required(allowed_roles=['Admin'])
def admin_verification_dashboard(request):
    """Display pending organization verification requests"""
    pending_verifications = Profile.objects.filter(
        role='Organization',
        verification_status='pending'
    ).select_related('user').order_by('-verification_submitted_at')
    
    context = {
        'pending_verifications': pending_verifications,
    }
    return render(request, 'admin_verification_dashboard.html', context)


@login_required
@role_required(allowed_roles=['Admin'])
def approve_organization(request, profile_id):
    """Approve an organization verification request"""
    if request.method == 'POST':
        try:
            profile = Profile.objects.select_related('user').get(
                id=profile_id,
                verification_status='pending'
            )

            # ✅ Update verification status
            profile.verification_status = 'verified'
            profile.verified_at = timezone.now()
            profile.save()

            # ✅ Create notification for the organization
            org_name = profile.org_name or profile.user.get_full_name() or profile.user.username

            Notification.objects.create(
                recipient=profile.user,
                sender=request.user,
                notification_type='verification_approved',
                title='Organization Verification Approved',
                message=(
                    f'Your organization "{org_name}" has been verified. '
                    f'You can now post opportunities and access all organization features.'
                ),
            )

            messages.success(
                request,
                f'Organization "{org_name}" has been verified.'
            )

        except Profile.DoesNotExist:
            messages.error(request, 'Organization not found or already processed.')

        return redirect('admin_verification_dashboard')

    return redirect('admin_verification_dashboard')



@login_required
@role_required(allowed_roles=['Admin'])
def reject_organization(request, profile_id):
    """Reject an organization verification request"""
    if request.method == 'POST':
        try:
            profile = Profile.objects.select_related('user').get(
                id=profile_id,
                verification_status='pending',
            )

            rejection_reason = request.POST.get('rejection_reason', '')

            # Update profile status
            profile.verification_status = 'rejected'
            profile.verification_reason = rejection_reason
            profile.save()

            # ✅ Send notification to the organization
            Notification.objects.create(
                recipient=profile.user,
                notification_type='verification_rejected',
                title='Organization Verification Rejected',
                message=(
                    f'Your verification request was rejected. '
                    f'Reason: {rejection_reason or "No reason provided."}'
                ),
            )

            messages.success(
                request,
                f'Organization "{profile.org_name or profile.user.get_full_name()}" has been rejected.',
            )

        except Profile.DoesNotExist:
            messages.error(request, 'Organization not found or already processed.')

        return redirect('admin_verification_dashboard')

    return redirect('admin_verification_dashboard')


# --- Notifications (Tabbed: All / Archive / Favorite) ---
@login_required
def notifications(request):
    tab = request.GET.get('tab', 'all')

    # Mark all non-archived notifications as read when opening the page
    Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).update(read=True)

    base_qs = Notification.objects.filter(recipient=request.user)

    # Filter which list to show
    if tab == 'favorite':
        notifications_qs = base_qs.filter(is_favorite=True, is_archived=False)
    elif tab == 'archive':
        notifications_qs = base_qs.filter(is_archived=True)
    else:  # 'all'
        notifications_qs = base_qs.filter(is_archived=False)

    notifications_qs = notifications_qs.order_by('-timestamp')

    # ✅ Counts for badges
    unread_count = base_qs.filter(read=False, is_archived=False).count()
    favorite_count = base_qs.filter(is_favorite=True, is_archived=False).count()
    archive_count = base_qs.filter(is_archived=True).count()

    context = {
        'notifications': notifications_qs,
        'unread_count': unread_count,
        'favorite_count': favorite_count,
        'archive_count': archive_count,
        'active_tab': tab,
    }
    return render(request, 'notifications.html', context)





@login_required
@require_POST
def notification_toggle_favorite(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_favorite = not notif.is_favorite  # toggle favorite on/off
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))



@login_required
@require_POST
def notification_archive(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_archived = True
    notif.read = True
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))


@login_required
@require_POST
def notification_delete(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))


@login_required
@require_POST
def notification_mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).update(read=True)
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))

@login_required
def org_profile(request):
    """Load the single-page organization profile UI."""
    profile = request.user.profile  # should always exist for logged-in org

    # Unread notification count (ignoring archived)
    unread_count = Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).count()

    # Recent notifications for dropdown
    recent_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-timestamp')[:5]

    context = {
        "user": request.user,
        "profile": profile,
        "unread_count": unread_count,
        "notifications": recent_notifications,
    }
    return render(request, "org_profile.html", context)


@login_required
def save_org_profile(request):
    """AJAX endpoint for updating the organization profile."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    profile = request.user.profile
    errors = {}

    def get_clean(field):
        return request.POST.get(field, "").strip()

    # --- Validation helpers ---
    import re
    url_regex = re.compile(r'^(https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*|[a-zA-Z0-9._-]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def valid_url(value):
        return value == "" or url_regex.match(value)

    def valid_email(value):
        return value == "" or email_regex.match(value)

    # --- Update fields (use existing value if empty) ---
    profile.org_name = get_clean("org_name") or profile.org_name
    profile.description = get_clean("description") or profile.description
    profile.mission = get_clean("mission") or profile.mission
    profile.department = get_clean("department") or profile.department
    profile.website = get_clean("website") or profile.website
    profile.address = get_clean("address") or profile.address

    profile.contact_email = get_clean("contact_email") or profile.contact_email
    profile.contact_phone = get_clean("contact_phone") or profile.contact_phone

    profile.social_facebook = get_clean("social_facebook") or profile.social_facebook
    profile.social_instagram = get_clean("social_instagram") or profile.social_instagram
    profile.social_linkedin = get_clean("social_linkedin") or profile.social_linkedin

    profile.is_public = (request.POST.get("is_public") == "True")

    # --- Validation checks ---
    if not request.POST.get("org_name", "").strip():
        errors["org_name"] = "Organization name is required."

    contact_email = request.POST.get("contact_email", "").strip()
    if contact_email and not valid_email(contact_email):
        errors["contact_email"] = "Invalid email format. Please enter a valid email address."

    contact_phone = request.POST.get("contact_phone", "").strip()
    if contact_phone:
        philippine_phone_pattern = r'^(09|\+639|639)\d{9}$'
        if not re.match(philippine_phone_pattern, contact_phone):
            errors["contact_phone"] = (
                "Please enter a valid Philippine mobile number "
                "(e.g., 09123456789 or +639123456789)"
            )

    website = request.POST.get("website", "").strip()
    if website and not valid_url(website):
        errors["website"] = (
            "Invalid website URL. Please enter a full URL "
            "(e.g., https://www.yourwebsite.com) or just your domain."
        )

    social_links = {
        "facebook": request.POST.get("social_facebook", "").strip(),
        "instagram": request.POST.get("social_instagram", "").strip(),
        "linkedin": request.POST.get("social_linkedin", "").strip(),
    }
    for key, val in social_links.items():
        if val and not valid_url(val):
            errors[f"social_{key}"] = (
                f"Invalid {key.capitalize()} URL. Please enter a valid URL "
                f"(e.g., https://{key}.com/yourpage) or just your username."
            )

    # --- Logo upload (optional) ---
    if "org_logo" in request.FILES:
        logo = request.FILES["org_logo"]

        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if logo.content_type not in allowed_types:
            errors["org_logo"] = "Invalid file type. Please upload PNG, JPG, or WebP."

        if logo.size > 3 * 1024 * 1024:
            errors["org_logo"] = "File too large. Max file size is 3MB."

        if "org_logo" not in errors:
            profile.org_logo = logo

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # --- Save ---
    try:
        if "org_logo" in request.FILES:
            profile.profile_picture = profile.org_logo

        profile.save()
        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully!",
            "updated": {
                "org_name": profile.org_name,
                "logo_url": profile.org_logo.url if profile.org_logo else None,
                "profile_picture_url": profile.profile_picture.url if profile.profile_picture else None,
                "is_public": profile.is_public,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
@login_required
def student_notification(request):
    tab = request.GET.get('tab', 'all')

    # Mark all non-archived notifications as read when opening the page
    Notification.objects.filter(
        recipient=request.user,
        read=False,
        is_archived=False
    ).update(read=True)

    base_qs = Notification.objects.filter(recipient=request.user)

    # Filter which list to show
    if tab == 'favorite':
        notifications_qs = base_qs.filter(is_favorite=True, is_archived=False)
    elif tab == 'archive':
        notifications_qs = base_qs.filter(is_archived=True)
    else:  # 'all'
        notifications_qs = base_qs.filter(is_archived=False)

    notifications_qs = notifications_qs.order_by('-timestamp')

    # Counts for badges
    unread_count = base_qs.filter(read=False, is_archived=False).count()
    favorite_count = base_qs.filter(is_favorite=True, is_archived=False).count()
    archive_count = base_qs.filter(is_archived=True).count()

    context = {
        'notifications': notifications_qs,
        'unread_count': unread_count,
        'favorite_count': favorite_count,
        'archive_count': archive_count,
        'active_tab': tab,
    }
    # 👇 IMPORTANT: include the subfolder in the template path
    return render(request, 'student_notification.html', context)

