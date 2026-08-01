from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Complaint, ComplaintImage


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if request.user.profile.role != 'admin':
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('user_dashboard')
        except Profile.DoesNotExist:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    return render(request, 'Home_page.html')


def about_us(request):
    return render(request, 'About_us.html')


def contact_us(request):
    return render(request, 'Contact_us.html')


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
            if user.profile.account_status != 'active':
                messages.error(request, 'Your account has been disabled. Please contact support.')
                return redirect('login')
            login(request, user)
            role = user.profile.role
            if role == 'admin':
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    last_message = None
    if request.method == 'GET':
        storage = messages.get_messages(request)
        messages_list = list(storage)
        if messages_list:
            last_message = messages_list[-1]
    
    return render(request, 'Login.html', {
        'last_message': last_message,
    })


@login_required(login_url='/login/')
def user_dashboard(request):
    user = request.user
    complaints = Complaint.objects.filter(user=user)
    total_complaints = complaints.count()
    in_progress_count = complaints.filter(status='in_progress').count()
    resolved_count = complaints.filter(status='resolved').count()
    closed_count = complaints.filter(status='rejected').count()
    recent_complaints = complaints.order_by('-created_at')[:5]
    return render(request, 'Dashboard.html', {
        'full_name': display_name(request.user),
        'total_complaints': total_complaints,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'recent_complaints': recent_complaints,
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
    messages.success(request, 'You have been logged out successfully.')
    last_message = None
    storage = messages.get_messages(request)
    messages_list = list(storage)
    if messages_list:
        last_message = messages_list[-1]
    
    return render(request, 'Logedout.html', {
        'last_message': last_message,
    })


@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            request.session['password_changed'] = True
            return redirect('change_password')

    show_success = request.session.pop('password_changed', False)
    return render(request, 'Change_password.html', {
        'full_name': display_name(request.user),
        'show_success': show_success,
    })


@login_required(login_url='/login/')
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'My_complaint.html', {
        'full_name': display_name(request.user),
        'complaints': complaints,
    })


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
            landmark=request.POST.get('landmark', '').strip(),
            latitude=latitude,
            longitude=longitude,
            is_anonymous=request.POST.get('is_anonymous') == 'on',
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
    messages.success(request, 'Complaint submitted successfully.')
    return render(request, 'Complained_Successfully.html', {
        'complaint': complaint,
    })


@login_required(login_url='/login/')
def complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, user=request.user)
    return render(request, 'Status_Result.html', {
        'full_name': display_name(request.user),
        'complaint': complaint,
    })


# ===================== ADMIN VIEWS =====================

@admin_required
def admin_dashboard(request):
    complaints = Complaint.objects.all()
    total_complaints = complaints.count()
    in_progress_count = complaints.filter(status='in_progress').count()
    resolved_count = complaints.filter(status='resolved').count()
    closed_count = complaints.filter(status='rejected').count()
    recent_complaints = complaints.order_by('-created_at')[:5]
    return render(request, 'A_Dashboard.html', {
        'full_name': display_name(request.user),
        'total_complaints': total_complaints,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'recent_complaints': recent_complaints,
    })


@admin_required
def admin_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if search_query:
        complaints = complaints.filter(complaint_id__icontains=search_query) | \
                     complaints.filter(description__icontains=search_query) | \
                     complaints.filter(user__email__icontains=search_query)

    return render(request, 'A_complaints.html', {
        'full_name': display_name(request.user),
        'complaints': complaints,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    })


@admin_required
def admin_users(request):
    users = User.objects.filter(profile__role='user').order_by('-date_joined')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    if status_filter:
        users = users.filter(profile__account_status=status_filter)
    if search_query:
        users = users.filter(email__icontains=search_query) | \
               users.filter(first_name__icontains=search_query)

    return render(request, 'A_Users.html', {
        'full_name': display_name(request.user),
        'users': users,
        'status_filter': status_filter,
        'search_query': search_query,
    })


@admin_required
def admin_complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    images = complaint.images.all()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Complaint.STATUS_CHOICES):
            complaint.status = new_status
            complaint.save()
            messages.success(request, f'Complaint {complaint_id} status updated to {complaint.get_status_display()}.')
            return redirect('admin_complaint_detail', complaint_id=complaint_id)

    return render(request, 'A_complaintdetail.html', {
        'full_name': display_name(request.user),
        'complaint': complaint,
        'images': images,
    })


@admin_required
def admin_assign_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    admins = User.objects.filter(profile__role='admin')

    if request.method == 'POST':
        officer_id = request.POST.get('officer')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')
        note = request.POST.get('note')
        
        if not officer_id:
            messages.error(request, 'Please select an officer to assign.')
            return redirect('admin_assign_complaint', complaint_id=complaint_id)
        
        messages.success(request, f'Complaint {complaint_id} has been assigned successfully.')
        return redirect('admin_complaints')

    return render(request, 'A_assigncomplain.html', {
        'full_name': display_name(request.user),
        'complaint': complaint,
        'admins': admins,
    })


@admin_required
def admin_profile(request):
    profile = request.user.profile
    return render(request, 'A_profile.html', {
        'full_name': display_name(request.user),
        'email': request.user.email,
        'phone': profile.phone,
        'account_status': profile.account_status,
        'last_login': request.user.last_login,
        'member_since': request.user.date_joined,
    })


@admin_required
def admin_reports(request):
    complaints = Complaint.objects.all()
    category_filter = request.GET.get('category', '')

    if category_filter:
        complaints = complaints.filter(category=category_filter)

    total_complaints = complaints.count()
    in_progress_count = complaints.filter(status='in_progress').count()
    resolved_count = complaints.filter(status='resolved').count()
    closed_count = complaints.filter(status='rejected').count()

    monthly_counts = [0] * 12
    for c in complaints:
        month = c.created_at.month - 1
        monthly_counts[month] += 1

    return render(request, 'A_reports.html', {
        'full_name': display_name(request.user),
        'total_complaints': total_complaints,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'monthly_counts': monthly_counts,
        'category_filter': category_filter,
        'category_choices': Complaint.CATEGORY_CHOICES,
    })


@admin_required
def admin_change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('admin_profile')

    return render(request, 'A_change_password.html', {
        'full_name': display_name(request.user),
    })


@admin_required
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.profile.role == 'admin':
            messages.error(request, 'Cannot change status of another admin.')
            return redirect('admin_users')
        if user.profile.account_status == 'active':
            user.profile.account_status = 'inactive'
            messages.success(request, f'Account for {user.email} has been disabled.')
        else:
            user.profile.account_status = 'active'
            messages.success(request, f'Account for {user.email} has been enabled.')
        user.profile.save()
    return redirect('admin_users')


@admin_required
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'A_logedout.html')
