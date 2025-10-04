# MyLogin/views.py
import bcrypt
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .supabase_client import supabase

# ----------------------------
# REGISTER VIEW
# ----------------------------
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        else:
            # Check if email already exists in Supabase
            existing = supabase.table("users").select("*").eq("email", email).execute()
            if existing.data:
                messages.error(request, "Email already registered")
            else:
                # Hash the password before storing
                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                supabase.table("users").insert({
                    "name": name,
                    "email": email,
                    "password_hash": hashed
                }).execute()
                messages.success(request, "Account created successfully! Please login.")
                return redirect("login")

    return render(request, "MyLogin/register.html")


# ----------------------------
# LOGIN VIEW
# ----------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Get user by email
        response = supabase.table("users").select("*").eq("email", email).execute()

        if response.data:
            user = response.data[0]
            # Compare hashed password
            if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                request.session['user'] = user
                return redirect("home")
        messages.error(request, "Invalid email or password")

    return render(request, "MyLogin/login.html")


# ----------------------------
# HOME VIEW
# ----------------------------
def home_view(request):
    user = request.session.get('user')
    if user:
        return HttpResponse(f"Welcome, {user['name']}! <a href='/logout/'>Logout</a>")
    else:
        return redirect("login")


# ----------------------------
# LOGOUT VIEW
# ----------------------------
def logout_view(request):
    request.session.flush()  # clear session
    return redirect("login")
