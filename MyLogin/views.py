from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from supabase import create_client, Client
from decouple import config

# Initialize Supabase
SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_KEY = config("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def register_view(request):
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check if email already exists
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            messages.error(request, "Email is already registered.")
            return redirect("register")

        # Hash the password
        hashed_password = make_password(password)

        # ✅ Fix role to match database allowed values
        if role == "org":
            role = "organization"
        elif role == "stud":
            role = "student"
        elif role not in ["student", "organization", "admin"]:
            role = "student"  # default fallback

        # Insert user into Supabase
        try:
            response = supabase.table("users").insert({
                "email": email,
                "password_hash": hashed_password,
                "name": name,
                "role": role,
            }).execute()

            if response.data:
                messages.success(request, "Registration successful! Please log in.")
                return redirect("login")
            else:
                messages.error(request, f"Error: {response}")
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, "MyLogin/register.html")


def login_view(request):
    return render(request, "MyLogin/login.html")
