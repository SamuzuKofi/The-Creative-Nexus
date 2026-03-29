from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
] + router.urls
