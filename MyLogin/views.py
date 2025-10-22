from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from .models import Profile
from datetime import datetime
from .models import Profile        # Profile is in MyLogin
from Myapp.models import Posting    # Posting is in Myapp


# --- Session timeout (10 minutes AFK limit) ---
SESSION_TIMEOUT = 600  # 600 seconds = 10 minutes


def login_view(request):
    # ✅ Check if redirected after inactivity
    if request.method == 'GET' and 'session_expired' in request.GET:
        messages.warning(request, "You were logged out due to inactivity.")

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.session['last_activity'] = timezone.now().timestamp()

            # --- Redirect based on role ---
            if hasattr(user, 'profile'):
                if user.profile.role == "Student":
                    return redirect('student_dashboard')
                elif user.profile.role == "Organization":
                    return redirect('organization_dashboard')
            # fallback if no profile or unknown role
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


from django.utils import timezone

def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    last_activity = request.session.get('last_activity')
    now = timezone.now()

    if last_activity:
        # ✅ Convert ISO string back to datetime object
        last_activity = datetime.fromisoformat(last_activity)
        elapsed = (now - last_activity).total_seconds()

        if elapsed > SESSION_TIMEOUT:
            logout(request)
            messages.warning(request, "You were logged out due to inactivity.")
            return redirect(f"{reverse('login')}?session_expired=1")

    # ✅ Store current time as ISO string
    request.session['last_activity'] = now.isoformat()

    return render(request, 'student_dashboard.html')


@login_required
def profile(request):
    return render(request, 'profile.html')

def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        org_name = request.POST.get('org_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Email already exists check
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Create user
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

    return render(request, 'org_dashboard.html')


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

        # Optional: validate title and deadline
        if not title:
            messages.error(request, "Title is required.")
            return redirect('edit_posting', post_id=post_id)
        
        posting.title = title
        posting.description = description
        posting.deadline = deadline
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

    return render(request, 'delete_posting.html', {'posting': posting})