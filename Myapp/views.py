from django.shortcuts import render, redirect, get_object_or_404 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Application, Posting, Profile 

def organizationDashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    postings = Posting.objects.filter(organization=request.user)
    applications = Application.objects.filter(posting__organization=request.user)
    
    return render(request, "Myapp/organizationDashboard.html", {
        'postings': postings,
        'applications': applications
    })

def my_applications(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    applications = Application.objects.filter(student=request.user)
    
    return render(request, "Myapp/my_applications.html", {
        'applications': applications
    })

def create_application(request, posting_id):
    if not request.user.is_authenticated:
        return redirect("login")
    
    posting = get_object_or_404(Posting, id=posting_id)
    
    if request.method == "POST":
        resume = request.FILES.get('resume')
        note = request.POST.get('note', '')
        
        if Application.objects.filter(student=request.user, posting=posting).exists():
            messages.error(request, "You have already applied to this posting.")
        else:
            application = Application.objects.create(
                student=request.user,
                posting=posting,
                resume=resume,
                note=note
            )
            messages.success(request, "Application submitted successfully!")
            return redirect('my_applications')
    
    return render(request, "Myapp/create_application.html", {'posting': posting})

def withdraw_application(request, application_id):
    if not request.user.is_authenticated:
        return redirect("login")
    
    application = get_object_or_404(Application, id=application_id, student=request.user)
    
    if application.status in ['submitted', 'under_review']:
        application.status = 'withdrawn'
        application.save()
        messages.success(request, "Application withdrawn successfully.")
    else:
        messages.error(request, "Cannot withdraw this application.")
    
    return redirect('my_applications')

# 🏠 Home view
def home_view(request):
    return redirect("login")


# 🔐 Login view (email-based)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("studentDashboard")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "Myapp/login.html")


# 🧾 Register view
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
        else:
            username = email.split("@")[0]
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = name
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")

    return render(request, "Myapp/register.html")


# 🧑‍🎓 Student Dashboard
def studentDashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "Myapp/studentDashboard.html")


# 👤 Profile view (requires login)
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "Myapp/profile.html")


# 🚪 Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")
