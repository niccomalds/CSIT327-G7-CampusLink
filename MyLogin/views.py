from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Profile  # import the Profile model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

# Login view with role-based redirect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
            if user:
                login(request, user)

                try:
                    role = user.profile.role
                except Profile.DoesNotExist:
                    role = None

                if role == "Student":
                    return redirect('student_dashboard')
                elif role == "Organization":
                    return redirect('organization_dashboard')
                else:
                    messages.warning(request, "No role assigned. Redirecting to home.")
                    return redirect('home')

            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, 'login.html')


# Updated Register view with role-specific fields
def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'Student')

        # Role-based fields
        if role == "Student":
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            org_name = ''
        else:
            first_name = ''
            last_name = ''
            # Match the HTML input name for organization
            org_name = request.POST.get('org_name', '').strip()

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = {}

        # Validation
        if role == "Student":
            if not first_name:
                errors['first_name'] = 'First name is required'
            if not last_name:
                errors['last_name'] = 'Last name is required'
        else:
            if not org_name:
                errors['org_name'] = 'Organization name is required'

        if not email:
            errors['email'] = 'Email is required'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'

        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'

        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'

        if errors:
            return render(request, 'register.html', {
                'errors': errors,
                'role': role,
                'first_name': first_name,
                'last_name': last_name,
                'org_name': org_name,
                'email': email
            })

        # Create user
        username = email.split('@')[0]
        if role == "Student":
            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name)
        else:
            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=org_name)

        # Create profile
        Profile.objects.create(user=user, role=role)

        messages.success(request, f'Account created successfully as {role}! Please login.')
        return redirect('login')

    # GET request
    return render(request, 'register.html', {
        'role': 'Student',
        'first_name': '',
        'last_name': '',
        'org_name': '',
        'email': '',
        'errors': {}
    })


# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')


# Home view (fallback)
def home_view(request):
    return render(request, 'home.html')


@login_required
def student_dashboard_view(request):
    return render(request, 'student_dashboard.html')


def organization_dashboard(request):
    return render(request, 'organization_dashboard.html')


@login_required
def profile(request):
    return render(request, 'profile.html')
