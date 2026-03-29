"""
URL configuration for the_creative_nexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/settings/#root-urlconf
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.template_views import (
    home, dashboard, portfolio_view, profile_view, collaborations_view,
    explore_view, register_view, login_view, logout_view, verify_email_view,
    notifications_view, projects_view, project_detail
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
    path('notifications/', notifications_view, name='notifications'),
    path('projects/', projects_view, name='projects'),
    path('projects/<int:project_id>/', project_detail, name='project-detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/verify-email/', verify_email_view, name='verify-email'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/core/', include('core.urls')),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
]

# Temporary workaround to serve media files locally while testing with DEBUG=False
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
