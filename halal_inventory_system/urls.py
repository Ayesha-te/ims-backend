"""
URL configuration for halal_inventory_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from inventory.auth_views import register_supermarket, login_supermarket

# Customize admin site header and title
admin.site.site_header = "Halal Inventory Management System"
admin.site.site_title = "Halal IMS Admin"
admin.site.index_title = "Welcome to Halal Inventory Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    # Direct fallback auth endpoints for compatibility
    path('auth/register/', register_supermarket, name='auth_register_fallback'),
    path('auth/login/', login_supermarket, name='auth_login_fallback'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
