from django.contrib import admin
from django.urls import path
from main.views import home, login_view

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('admin/', admin.site.urls),
]
