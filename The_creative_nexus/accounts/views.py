from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
import threading
import logging

from .models import CustomUser, UserProfile
from .serializers import (
    CustomUserSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileUpdateSerializer
)


class RegisterView(views.APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate email verification token
            token = ''.join(secrets.choice(
                string.ascii_letters + string.digits) for _ in range(32))
            user.email_verification_token = token
            user.save()

            # Send verification email
            verification_link = f"{request.build_absolute_uri('/api/accounts/verify-email/')}?token={token}"

            def send_verification_email():
                try:
                    send_mail(
                        'Verify Your Email - The Creative Nexus',
                        f'Please click the link to verify your email: {verification_link}',
                        getattr(settings, 'DEFAULT_FROM_EMAIL',
                                'sedemkofiamuzu@gmail.com'),
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logging.getLogger(__name__).error(
                        "Verification email sending failed: %s", e)

            # Run in a background thread to prevent blocking the web request
            threading.Thread(target=send_verification_email,
                             daemon=True).start()

            return Response(
                {'message': 'Registration successful. Please check your email to verify your account.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(views.APIView):
    """Email verification endpoint"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        try:
            user = CustomUser.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = ''
            user.save()
            return Response({'message': 'Email verified successfully'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.email_verified:
                return Response(
                    {'error': 'Please verify your email before logging in'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': CustomUserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class CurrentUserView(views.APIView):
    """Get current authenticated user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ViewSet):
    """User profile management"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all user profiles"""
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a specific user profile"""
        try:
            profile = UserProfile.objects.get(user_id=pk)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        """Update current user profile"""
        if request.user.id != int(pk):
            return Response(
                {'error': 'You can only update your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = request.user.profile
        serializer = UserProfileUpdateSerializer(
            profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by role, skills, or location"""
        query = request.query_params.get('q', '')
        role = request.query_params.get('role')

        profiles = UserProfile.objects.all()

        if role:
            profiles = profiles.filter(role=role)

        if query:
            profiles = profiles.filter(
                skills__icontains=query
            ) | profiles.filter(
                user__username__icontains=query
            ) | profiles.filter(
                location__icontains=query
            )

        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)
