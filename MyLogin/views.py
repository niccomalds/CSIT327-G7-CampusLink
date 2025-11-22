from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from Myapp.models import Posting
from .models import Profile
from Myapp.utils import can_user_apply
from django.contrib.admin.views.decorators import staff_member_required

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
            Profile.objects.create(user=user, role=role, org_name=org_name)
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
    return render(request, 'student_dashboard.html')


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
    }
    
    context = {
        'profile': profile,
        'postings': postings,
        'active_postings_count': active_postings_count,
        'total_applicants': total_applicants,
        'total_views': total_views,
        'acceptance_rate': acceptance_rate,
        'recent_postings': postings.order_by('-id'),
        'today': date.today(),
        **verification_context
    }
    return render(request, 'org_dashboard.html', context)


@login_required
@role_required(allowed_roles=['Admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


# --- Profile ---
@login_required
def profile(request):
    return render(request, 'profile.html', {
        "profile": request.user.profile
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile

        profile.full_name = request.POST.get('full_name', profile.full_name)
        profile.email = request.POST.get('email', profile.email)
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

    return render(request, 'manage_posting.html', {'postings': postings})


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


@login_required
def post_opportunity(request):
    return render(request, 'post_opportunity.html')


# --- Student Applications ---
@login_required
@role_required(allowed_roles=['Student'])
def my_applications(request):
    # Currently empty, dynamic data can be loaded later
    applications = []
    return render(request, 'my_applications.html', {'applications': applications})


# --- Organization Applicants ---
@login_required
def applicants_list(request):
    return render(request, 'applicants_list.html')


# --- Organization Profile & Settings ---
@login_required
def org_profile(request):
    return render(request, 'org_profile.html')


@login_required
def org_settings(request):
    return render(request, 'org_settings.html')


# --- Settings & Notifications ---
@login_required
def settings_view(request):
    return render(request, 'settings.html')


def notifications(request):
    return render(request, 'notifications.html')


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

# === ADMIN VERIFICATION VIEWS ===

@staff_member_required
@role_required(allowed_roles=['Admin'])
def admin_verification_dashboard(request):
    """Admin dashboard for managing organization verifications"""
    # Get organizations pending verification
    pending_verifications = Profile.objects.filter(
        role='Organization', 
        verification_status='pending'
    ).select_related('user')
    
    # Get recent verification activity
    recent_activity = Profile.objects.filter(
        role='Organization'
    ).exclude(verification_status='unverified').order_by('-verification_submitted_at')[:10]
    
    context = {
        'pending_verifications': pending_verifications,
        'recent_activity': recent_activity,
        'pending_count': pending_verifications.count(),
    }
    return render(request, 'MyLogin/admin_verification_dashboard.html', context)

@staff_member_required
@role_required(allowed_roles=['Admin'])
def admin_verify_organization(request, profile_id):
    """Admin view to verify an organization"""
    try:
        profile = Profile.objects.get(id=profile_id, role='Organization')
    except Profile.DoesNotExist:
        messages.error(request, "Organization profile not found.")
        return redirect('admin_verification_dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        
        if action == 'approve':
            profile.verification_status = 'verified'
            profile.verified_at = timezone.now()
            profile.verification_reason = "Approved by administrator"
            profile.save()
            messages.success(request, f"{profile.org_name} has been verified successfully!")
            
        elif action == 'reject':
            profile.verification_status = 'rejected'
            profile.verification_reason = reason or "Verification rejected"
            profile.save()
            messages.warning(request, f"{profile.org_name} verification has been rejected.")
        
        return redirect('admin_verification_dashboard')
    
    context = {
        'profile': profile,
    }
    return render(request, 'MyLogin/admin_verify_organization.html', context)

@staff_member_required
@role_required(allowed_roles=['Admin'])
def admin_verification_stats(request):
    """API endpoint for verification statistics"""
    stats = {
        'total_organizations': Profile.objects.filter(role='Organization').count(),
        'verified_count': Profile.objects.filter(role='Organization', verification_status='verified').count(),
        'pending_count': Profile.objects.filter(role='Organization', verification_status='pending').count(),
        'rejected_count': Profile.objects.filter(role='Organization', verification_status='rejected').count(),
        'unverified_count': Profile.objects.filter(role='Organization', verification_status='unverified').count(),
    }
    return JsonResponse(stats)
