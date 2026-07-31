from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile

def home(request):
    return render(request, 'Home_page.html')

def display_name(user):
    try:
        return user.profile.full_name or user.first_name
    except Profile.DoesNotExist:
        return user.first_name or user.username

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not (full_name and email and phone and password):
            messages.error(request, 'All fields are required')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists')
            return redirect('signup')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name,
        )
        Profile.objects.create(user=user, role='user', phone=phone, full_name=full_name)
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')

    return render(request, 'Signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            role = user.profile.role
            if role == 'admin':
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'Login.html')

@login_required(login_url='/login/')
def user_dashboard(request):
    return render(request, 'Dashboard.html', {
        'full_name': display_name(request.user),
    })

@login_required(login_url='/login/')
def profile_view(request):
    profile = request.user.profile
    return render(request, 'Profile.html', {
        'full_name': display_name(request.user),
        'email': request.user.email,
        'phone': profile.phone,
        'account_status': profile.account_status,
        'last_login': request.user.last_login,
        'member_since': request.user.date_joined,
    })

def logout_view(request):
    logout(request)
    return render(request, 'Logedout.html')

@login_required(login_url='/login/')
def admin_dashboard(request):
    return render(request, 'A_Dashboard.html')
