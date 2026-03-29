"""
URL configuration for the_creative_nexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/settings/#root-urlconf
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.template_views import (
    home, dashboard, portfolio_view, profile_view, collaborations_view,
    explore_view, register_view, login_view, logout_view, verify_email_view
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Template views
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('portfolio/<int:user_id>/', portfolio_view, name='view-portfolio'),
    path('profile/', profile_view, name='profile'),
    path('collaborations/', collaborations_view, name='collaborations'),
    path('explore/', explore_view, name='explore'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/verify-email/', verify_email_view, name='verify-email'),

    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/core/', include('core.urls')),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
