from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

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
            return redirect('student_dashboard')  # or your dashboard URL
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def student_dashboard(request):
    # ✅ If not logged in, redirect to login
    if not request.user.is_authenticated:
        return redirect('login')

    # ✅ Check inactivity
    last_activity = request.session.get('last_activity')
    now = timezone.now().timestamp()

    if last_activity and now - last_activity > SESSION_TIMEOUT:
        logout(request)
        return redirect(f"{reverse('login')}?session_expired=1")

    # Update last activity timestamp
    request.session['last_activity'] = now

    # Render the dashboard
    return render(request, 'student/dashboard.html')


@login_required
def profile(request):
    return render(request, 'profile.html')
