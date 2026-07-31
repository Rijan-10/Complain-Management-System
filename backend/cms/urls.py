from django.contrib import admin
from django.urls import path
from main.views import home, login_view, signup_view, logout_view, profile_view, user_dashboard, admin_dashboard

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('profile/', profile_view, name='profile'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('django-admin/', admin.site.urls),
]
