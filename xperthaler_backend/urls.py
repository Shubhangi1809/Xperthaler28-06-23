"""xperthaler_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from .views import *
from django.conf.urls.static import  static
from xperthaler_backend.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    re_path('', include('user.urls', namespace='user')),
    re_path('', include('survey.urls', namespace='survey')),
    re_path('', include('inhaler.urls', namespace='inhaler')),
    path('', home, name="home"),
    path('api/', include('api.urls', namespace='api')),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
