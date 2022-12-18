"""pocdashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    # path('login', views.login_user, name="login"),
    path('', views.login_user, name="login"),
    path('logout', views.logout_user, name='logout'),
    path("dashboard", login_required(function=views.dashboard, login_url="login"), name="dashboard"),
    path("download-file", views.fileErr, name="downloadfile"),
    re_path(r'^getDataForChart$', views.getDataForChart),
    path('__debug__/', include('debug_toolbar.urls')),
]
