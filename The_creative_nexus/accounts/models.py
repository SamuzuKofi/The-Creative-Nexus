from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# User Role Choices
ROLE_CHOICES = (
    ('creator', 'Creator'),
    ('client', 'Client'),
    ('mentor', 'Mentor'),
    ('admin', 'Admin'),
)


class CustomUser(AbstractUser):
    """Extended user model with role support"""
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(
        max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """User profile with role and additional information"""
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='creator')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # For creators/mentors
    skills = models.TextField(blank=True, null=True,
                              help_text="Comma-separated list of skills")
    years_experience = models.IntegerField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)

    # For all users
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"

    def get_role_display(self):
        return dict(ROLE_CHOICES).get(self.role, 'Unknown')


# Signal to auto-create UserProfile when CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new CustomUser is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when CustomUser is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_delete, sender=UserProfile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    """Delete the profile picture from storage when the user profile is deleted"""
    if instance.profile_picture:
        instance.profile_picture.delete(save=False)
