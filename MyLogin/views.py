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
from django.shortcuts import render, redirect, get_object_or_404

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
    
    context = {
        'postings_list': postings_list,
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
    }
    
    context = {
        'profile': profile,
        'postings': postings,
        'active_postings_count': active_postings_count,
        'total_applicants': total_applicants,
        'total_views': total_views,
        'acceptance_rate': acceptance_rate,
        'recent_postings': postings.order_by('-id')[:3],  # Limit to 3 recent postings
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
        profile.contact_email = request.POST.get('email', profile.contact_email)
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

# === ADMIN POSTING APPROVAL VIEWS ===

@staff_member_required
@role_required(allowed_roles=['Admin'])
def admin_posting_approval(request):
    """Admin dashboard for reviewing pending postings"""
    # Get postings pending approval, ordered by creation date (oldest first)
    pending_postings = Posting.objects.filter(
        approval_status='pending'
    ).select_related('organization', 'organization__profile').order_by('created_at')
    
    # Get recently approved/rejected for context
    recent_actions = Posting.objects.exclude(
        approval_status='pending'
    ).select_related('organization', 'organization__profile', 'approved_by').order_by('-approved_at')[:10]
    
    # Approval criteria checklist
    approval_criteria = [
        "Content is appropriate and professional",
        "Opportunity is valid and legitimate", 
        "Description is clear and complete",
        "Deadline is reasonable",
        "Organization is verified",
        "No spam or promotional content",
        "Complies with platform guidelines"
    ]
    
    context = {
        'pending_postings': pending_postings,
        'recent_actions': recent_actions,
        'page_title': 'Posting Approval Dashboard',
        'pending_count': pending_postings.count(),
        'approval_criteria': approval_criteria,
    }
    return render(request, 'MyLogin/admin_posting_approval.html', context)

@staff_member_required
@role_required(allowed_roles=['Admin'])
def approve_posting(request, posting_id):
    """Approve a specific posting"""
    posting = get_object_or_404(Posting, id=posting_id)
    
    if request.method == 'POST':
        # Get checklist results from form
        criteria_met = request.POST.get('criteria_met', '')
        additional_notes = request.POST.get('additional_notes', '')
        
        posting.approval_status = 'approved'
        posting.approved_by = request.user
        posting.approved_at = timezone.now()
        
        # Store approval notes if provided
        if additional_notes:
            posting.rejection_reason = f"Approval Notes: {additional_notes}"
        
        posting.save()
        
        messages.success(request, f'Posting "{posting.title}" has been approved and published.')
        return redirect('admin_posting_approval')
    
    # If not POST, show confirmation page with criteria checklist
    approval_criteria = [
        "Content is appropriate and professional",
        "Opportunity is valid and legitimate", 
        "Description is clear and complete",
        "Deadline is reasonable",
        "Organization is verified",
        "No spam or promotional content",
        "Complies with platform guidelines"
    ]
    
    context = {
        'posting': posting,
        'action': 'approve',
        'approval_criteria': approval_criteria,
    }
    return render(request, 'MyLogin/admin_approval_confirm.html', context)

@staff_member_required
@role_required(allowed_roles=['Admin'])
def reject_posting(request, posting_id):
    """Reject a specific posting"""
    posting = get_object_or_404(Posting, id=posting_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        criteria_violations = request.POST.getlist('criteria_violations')  # Get checklist of violations
        
        posting.approval_status = 'rejected'
        posting.approved_by = request.user
        posting.approved_at = timezone.now()
        
        # Build comprehensive rejection reason
        full_rejection_reason = rejection_reason
        if criteria_violations:
            violations_text = "Violations: " + ", ".join(criteria_violations)
            full_rejection_reason = f"{violations_text}. {rejection_reason}"
        
        posting.rejection_reason = full_rejection_reason
        posting.save()
        
        messages.warning(request, f'Posting "{posting.title}" has been rejected.')
        return redirect('admin_posting_approval')
    
    # Rejection criteria
    rejection_criteria = [
        "Inappropriate content",
        "Spam or promotional content", 
        "Unclear or incomplete description",
        "Unreasonable deadline",
        "Organization not verified",
        "Violates platform guidelines",
        "Duplicate posting",
        "Other (specify in notes)"
    ]
    
    context = {
        'posting': posting,
        'action': 'reject',
        'rejection_criteria': rejection_criteria,
    }
    return render(request, 'MyLogin/admin_approval_confirm.html', context)

@staff_member_required
@role_required(allowed_roles=['Admin'])
def posting_detail_modal(request, posting_id):
    """Return posting details for modal display"""
    posting = get_object_or_404(Posting, id=posting_id)
    return render(request, 'MyLogin/posting_detail_modal.html', {'posting': posting})

@staff_member_required
@role_required(allowed_roles=['Admin'])
def admin_posting_stats(request):
    """API endpoint for posting approval statistics"""
    stats = {
        'total_postings': Posting.objects.count(),
        'approved_count': Posting.objects.filter(approval_status='approved').count(),
        'pending_count': Posting.objects.filter(approval_status='pending').count(),
        'rejected_count': Posting.objects.filter(approval_status='rejected').count(),
    }
    return JsonResponse(stats)

@login_required
@role_required(allowed_roles=['Organization'])
def post_opportunity(request):

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline_str = request.POST.get('deadline')

        # ⭐ TAGS
        selected_tags = request.POST.getlist("tags")
        tags_str = ",".join(selected_tags)

        # --- VALIDATION ---
        if not (title and description and deadline_str):
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

        # --- CREATE POSTING ---
        Posting.objects.create(
            organization=request.user,
            title=title,
            description=description,
            deadline=deadline,
            tags=tags_str,
            approval_status='pending'
        )

        messages.success(request, "Opportunity created successfully! Waiting for admin approval.")
        return redirect('organization_dashboard')

    return render(request, 'post_opportunity.html')



@login_required
def org_profile(request):
    """Load the single-page organization profile UI."""
    profile = request.user.profile  # always exists
    context = {
        "user": request.user,
        "profile": profile,
    }
    return render(request, "org_profile.html", context)


@login_required
def save_org_profile(request):
    """Optimized AJAX endpoint for updating the organization profile securely."""

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    profile = request.user.profile
    errors = {}

    # Simple helper
    def get_clean(field):
        return request.POST.get(field, "").strip()

    # ---------------------------
    # VALIDATION HELPERS
    # ---------------------------
    import re
    url_regex = re.compile(r'^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$')
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def valid_url(value):
        return value == "" or url_regex.match(value)

    def valid_email(value):
        return value == "" or email_regex.match(value)

    # ---------------------------
    # CLEAN INPUTS
    # ---------------------------
    profile.org_name = get_clean("org_name") or profile.org_name
    profile.description = get_clean("description")
    profile.mission = get_clean("mission")
    profile.department = get_clean("department")
    profile.website = get_clean("website")
    profile.address = get_clean("address")

    profile.contact_email = get_clean("contact_email")
    profile.contact_phone = get_clean("contact_phone")

    profile.social_facebook = get_clean("social_facebook")
    profile.social_instagram = get_clean("social_instagram")
    profile.social_linkedin = get_clean("social_linkedin")

    profile.is_public = (request.POST.get("is_public") == "True")

    # ---------------------------
    # VALIDATION CHECKS
    # ---------------------------
    if not profile.org_name:
        errors["org_name"] = "Organization name is required."

    if profile.contact_email and not valid_email(profile.contact_email):
        errors["contact_email"] = "Invalid email format."

    if profile.website and not valid_url(profile.website):
        errors["website"] = "Invalid website URL."

    # Validate social links
    social_fields = {
        "facebook": profile.social_facebook,
        "instagram": profile.social_instagram,
        "linkedin": profile.social_linkedin,
    }
    for key, val in social_fields.items():
        if val and not valid_url(val):
            errors[f"social_{key}"] = f"Invalid {key.capitalize()} URL."

    # ---------------------------
    # LOGO UPLOAD (optional)
    # ---------------------------
    if "org_logo" in request.FILES:
        logo = request.FILES["org_logo"]

        # Allow only safe image types
        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if logo.content_type not in allowed_types:
            errors["org_logo"] = "Invalid file type. Please upload PNG, JPG, or WebP."

        # Max size 3MB
        if logo.size > 3 * 1024 * 1024:
            errors["org_logo"] = "File too large. Max file size is 3MB."

        if "org_logo" not in errors:
            profile.org_logo = logo

    # If validation errors → return safely
    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    # ---------------------------
    # SAVE (atomic)
    # ---------------------------
    try:
        profile.save()
        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully!",
            "updated": {
                "org_name": profile.org_name,
                "logo_url": profile.org_logo.url if profile.org_logo else None,
                "is_public": profile.is_public,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

