from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from main.views import (home, about_us, contact_us, login_view, signup_view, logout_view, profile_view,
                        user_dashboard, admin_dashboard, new_complaint, complaint_success,
                        complaint_status, my_complaints, admin_complaints, admin_users, admin_complaint_detail,
                        admin_assign_complaint, admin_complaint_delete, admin_profile, admin_reports,
                        admin_change_password, admin_logout, admin_user_action, admin_add_admin,
                        admin_user_change_password, forgot_password, change_password)

urlpatterns = [
    path('', home, name='home'),
    path('about/', about_us, name='about'),
    path('contact/', contact_us, name='contact'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('my-complaints/', my_complaints, name='my_complaints'),
    path('new-complaint/', new_complaint, name='new_complaint'),
    path('complaint-success/<str:complaint_id>/', complaint_success, name='complaint_success'),
    path('complaint-status/<str:complaint_id>/', complaint_status, name='complaint_status'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/complaints/', admin_complaints, name='admin_complaints'),
    path('admin/complaints/<str:complaint_id>/', admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/complaints/<str:complaint_id>/assign/', admin_assign_complaint, name='admin_assign_complaint'),
    path('admin/complaints/<str:complaint_id>/delete/', admin_complaint_delete, name='admin_complaint_delete'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/users/add-admin/', admin_add_admin, name='admin_add_admin'),
    path('admin/users/<int:user_id>/action/', admin_user_action, name='admin_user_action'),
    path('admin/users/<int:user_id>/change-password/', admin_user_change_password, name='admin_user_change_password'),
    path('admin/profile/', admin_profile, name='admin_profile'),
    path('admin/reports/', admin_reports, name='admin_reports'),
    path('admin/change-password/', admin_change_password, name='admin_change_password'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('django-admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
