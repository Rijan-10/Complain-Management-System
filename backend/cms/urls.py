from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from main.views import (home, login_view, signup_view, logout_view, profile_view,
                        user_dashboard, admin_dashboard, new_complaint, complaint_success)

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('new-complaint/', new_complaint, name='new_complaint'),
    path('complaint-success/<str:complaint_id>/', complaint_success, name='complaint_success'),
    path('profile/', profile_view, name='profile'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('django-admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
