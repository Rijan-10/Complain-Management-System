from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Complaint, ComplaintImage

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
def new_complaint(request):
    if request.method == 'POST':
        category = request.POST.get('category', '')
        description = request.POST.get('description', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        photo_urls = [u.strip() for u in request.POST.getlist('photo_urls') if u.strip()]

        if not category:
            messages.error(request, 'Please select a category')
            return redirect('new_complaint')

        if not description:
            messages.error(request, 'Please describe your complaint')
            return redirect('new_complaint')

        if not photo_urls:
            messages.error(request, 'Please take a photo of the issue')
            return redirect('new_complaint')

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            messages.error(request, 'Location is required. Please allow location access and try again.')
            return redirect('new_complaint')

        complaint = Complaint.objects.create(
            user=request.user,
            category=category,
            description=description,
            latitude=latitude,
            longitude=longitude,
        )

        for url in photo_urls:
            ComplaintImage.objects.create(complaint=complaint, image_url=url)

        messages.success(request, 'Complaint submitted successfully')
        return redirect('complaint_success', complaint_id=complaint.complaint_id)

    return render(request, 'New_Complaint.html', {
        'cloudinary_cloud_name': settings.CLOUDINARY_CLOUD_NAME,
        'cloudinary_upload_preset': settings.CLOUDINARY_UNSIGNED_PRESET,
        'cloudinary_folder': settings.CLOUDINARY_FOLDER,
    })

@login_required(login_url='/login/')
def complaint_success(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, user=request.user)
    return render(request, 'Complained_Successfully.html', {
        'complaint': complaint,
    })

@login_required(login_url='/login/')
def admin_dashboard(request):
    return render(request, 'A_Dashboard.html')
