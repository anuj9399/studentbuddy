from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail


def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not name or not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect("/signup/")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("/signup/")

        # 👇 take only first name
        first_name = name.split()[0]

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )

        messages.success(request, "Account created! Please login.")
        return redirect("/login/")

    return render(request, "signup.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Username or password is incorrect")
            return redirect("/login/")

        login(request, user)

        next_url = request.GET.get("next", "/")
        return redirect(next_url)

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/")
