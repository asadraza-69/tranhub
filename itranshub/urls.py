"""itranshub URL Configuration

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include

from custom_auth.views import user_login
from user_management.views import main_dashboard, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', user_login, name='auth_login'),
    path('accounts/logout/', user_logout, name='auth_logout'),
    path('', main_dashboard, name='auth_login'),
    path('custom_auth/', include('custom_auth.urls')),
    path('loggings/', include('loggings.urls')),
    path('mail_config/', include('mail_config.urls')),
    path('user_management/', include('user_management.urls')),
    path('permissions/', include('permissions.urls')),
    path('itrans/', include('itrans.urls')),
    path('stripe_payments/', include('stripe_payments.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)