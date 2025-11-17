from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from datetime import datetime
from .models import Profile        # Profile is in MyLogin
from Myapp.models import Posting    # Posting is in Myapp
from datetime import date
from functools import wraps
from django.http import JsonResponse
from Myapp.utils import can_user_apply


# --- Session timeout (10 minutes AFK limit) ---
SESSION_TIMEOUT = 600  # 600 seconds = 10 minutes

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

# --- Authentication views ---
def login_view(request):
    if request.method == 'GET' and 'session_expired' in request.GET:
        messages.warning(request, "You were logged out due to inactivity.")

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')  # get the role selected in the form

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if hasattr(user, 'profile') and user.profile.role != selected_role:
                messages.error(request, "Access denied. Wrong role selected.")
                return redirect('login')

            login(request, user)
            request.session['last_activity'] = timezone.now().timestamp()

            # Redirect based on actual role
            if hasattr(user, 'profile'):
                if user.profile.role == "Student":
                    return redirect('student_dashboard')
                elif user.profile.role == "Organization":
                    return redirect('organization_dashboard')
                elif user.profile.role == "Admin":
                    return redirect('admin_dashboard')

            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# --- Dashboard views ---
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
    # Only allow Organization users
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Organization":
        messages.error(request, "Access denied.")
        return redirect('login')

    return render(request, 'org_dashboard.html')


@login_required
@role_required(allowed_roles=['Admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')  # create this template


# --- Other views ---
@login_required
def profile(request):
    profile = request.user.profile  # load the user's saved profile

    return render(request, 'profile.html', {
        "profile": profile
    })



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


def home_view(request):
    return render(request, 'home.html')

from django.contrib.auth.decorators import login_required


@login_required
def organization_dashboard(request):
    # Only allow Organization users
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Organization":
        messages.error(request, "Access denied.")
        return redirect('login')

    # Get organization's postings
    postings = Posting.objects.filter(organization=request.user)
    
    # Calculate stats
    active_postings_count = postings.filter(deadline__gte=date.today(), status='Active').count()
    total_applicants = 0
    total_views = 0
    acceptance_rate = 0
    
    # Get recent postings - SHOW ALL (remove the [:3] limit)
    recent_postings = postings.order_by('-id')  # ← REMOVED: [:3]

    context = {
        'active_postings_count': active_postings_count,
        'total_applicants': total_applicants,
        'total_views': total_views,
        'acceptance_rate': acceptance_rate,
        'recent_postings': recent_postings,
        'today': date.today(),
    }

    return render(request, 'org_dashboard.html', context)


# --- Organization/Admin Posting Management ---
@login_required
def manage_postings(request):
    # Only allow Organization or Admin
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

    # Only allow owner organization or admin
    if request.user.profile.role == "Organization" and posting.organization != request.user:
        messages.error(request, "Access denied.")
        return redirect('manage_postings')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        status = request.POST.get('status')  # ← ADD THIS LINE

        if not title:
            messages.error(request, "Title is required.")
            return redirect('edit_posting', post_id=post_id)
        
        posting.title = title
        posting.description = description
        posting.deadline = deadline
        posting.status = status  # ← ADD THIS LINE
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

    # Only allow owner organization or admin
    if request.user.profile.role == "Organization" and posting.organization != request.user:
        messages.error(request, "Access denied.")
        return redirect('manage_postings')

    if request.method == 'POST':
        posting.delete()
        messages.success(request, "Posting deleted successfully.")
        return redirect('manage_postings')

    # REDIRECT GET REQUESTS (since we deleted the template)
    return redirect('manage_postings')


@login_required
@role_required(allowed_roles=['Student'])
def my_applications(request):
    """
    Display the My Applications page for students
    """
    applications = []  # Empty for now - Mahinay will add real data later
    
    return render(request, 'my_applications.html', {
        'applications': applications
    })

@login_required
def applicants_list(request):
    return render(request, 'applicants_list.html')

@login_required
def org_profile(request):
    return render(request, 'org_profile.html')

@login_required
def org_settings(request):
    return render(request, 'org_settings.html')

@login_required
def post_opportunity(request):
    return render(request, 'post_opportunity.html')

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

        # ✅ Save uploaded image
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully.')

        return redirect('profile')

    return redirect('profile')


@login_required
def settings_view(request):
    return render(request, 'settings.html')

def notifications(request):
    return render(request, 'notifications.html')

def check_application_status(request, posting_id):
    """
    Check if user has already applied to a posting
    Returns JSON with application status
    """
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
