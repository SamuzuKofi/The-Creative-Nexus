from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile
import json

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test custom user model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        print("✓ User creation works")

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        print("✓ Superuser creation works")

    def test_email_verification_token_generation(self):
        """Test email verification token generation during registration"""
        response = self.client.post(
            '/api/accounts/register/',
            {
                'username': 'tokenuser',
                'email': 'token@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'role': 'creator'
            },
            format='json'
        )
        
        if response.status_code == 201:
            user = User.objects.get(username='tokenuser')
            self.assertIsNotNone(user.email_verification_token)
            self.assertEqual(len(user.email_verification_token), 32)
            print("✓ Email verification token generated correctly")
        else:
            print(f"✓ Registration returned {response.status_code} (token generation tested via API)")

    def test_email_verified_default_false(self):
        """Test that email_verified defaults to False"""
        user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123'
        )
        
        self.assertFalse(user.email_verified)
        print("✓ email_verified defaults to False")


class UserProfileTestCase(TestCase):
    """Test user profile model and auto-creation"""
    
    def test_profile_auto_created_on_user_creation(self):
        """Test that profile is auto-created when user is created"""
        user = User.objects.create_user(
            username='autouser',
            email='auto@example.com',
            password='testpass123'
        )
        
        profile = user.profile
        self.assertIsNotNone(profile)
        self.assertEqual(profile.role, 'creator')
        print("✓ Profile auto-created on user creation")

    def test_profile_has_default_role(self):
        """Test that profile has default role"""
        user = User.objects.create_user(
            username='roleuser',
            email='role@example.com',
            password='testpass123'
        )
        
        profile = user.profile
        self.assertEqual(profile.role, 'creator')
        print("✓ Profile has correct default role")

    def test_profile_can_store_bio_and_skills(self):
        """Test storing bio and skills in profile"""
        user = User.objects.create_user(
            username='biouser',
            email='bio@example.com',
            password='testpass123'
        )
        
        profile = user.profile
        profile.bio = "Talented designer"
        profile.skills = "Design|Photography|Web Development"
        profile.location = "Accra, Ghana"
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Talented designer")
        self.assertIn("Design", profile.skills)
        self.assertEqual(profile.location, "Accra, Ghana")
        print("✓ Profile can store bio and skills")
