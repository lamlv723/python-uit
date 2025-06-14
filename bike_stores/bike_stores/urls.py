"""
URL configuration for bike_stores project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.views import debug

urlpatterns = [
    # path('', debug.default_urlconf),  # root page
    path('', include('home.urls'), name='home'),  # root page
    path('admin/', admin.site.urls, name='admin'),
    path('api/production/', include('production.urls'), name='production'),
    path('api/sales/', include('sales.urls'), name='sales'),
    path('api/report/', include('report.urls'), name='report'),
]
