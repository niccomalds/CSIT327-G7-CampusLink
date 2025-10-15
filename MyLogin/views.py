from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from functools import wraps

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
    return render(request, 'org_dashboard.html')


@login_required
@role_required(allowed_roles=['Admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')  # create this template


# --- Other views ---
@login_required
def profile(request):
    return render(request, 'profile.html')


def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
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

        Profile.objects.create(user=user, role=role)
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


def home_view(request):
    return render(request, 'home.html')
