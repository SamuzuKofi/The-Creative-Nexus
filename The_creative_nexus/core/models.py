from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.exceptions import ValidationError
import threading

# Status choices for various models
PROJECT_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('in_progress', 'In Progress'),
    ('under_review', 'Under Review'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
)

COLLABORATION_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
)

MENTORSHIP_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('active', 'Active'),
    ('completed', 'Completed'),
)

# File size validator


def validate_file_size(value):
    """Ensure file size is not more than 50MB."""
    limit = 50 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 50 MB.')


class Portfolio(models.Model):
    """Artist portfolio to showcase their work"""
    CATEGORY_CHOICES = (
        ('visual_arts', 'Visual Arts'),
        ('design', 'Design'),
        ('animation', 'Animation'),
        ('photography', 'Photography'),
        ('filmmaking', 'Filmmaking'),
        ('music', 'Music'),
        ('writing', 'Writing'),
        ('tech', 'Technology'),
        ('mixed_media', 'Mixed Media'),
        ('other', 'Other'),
    )

    creator = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default='other', blank=True)
    cover_image = models.ImageField(
        upload_to='portfolio_covers/', blank=True, null=True)
    featured_work = models.ForeignKey(
        'CreativeWork', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_in')

    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.creator.username}'s Portfolio"


class CreativeWork(models.Model):
    """Individual creative asset/work uploaded by artists"""
    WORK_TYPE_CHOICES = (
        ('digital_art', 'Digital Art'),
        ('graphic_design', 'Graphic Design'),
        ('animation', 'Animation'),
        ('photography', 'Photography'),
        ('video', 'Video'),
        ('music', 'Music'),
        ('writing', 'Writing'),
        ('other', 'Other'),
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='works')
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name='works')

    title = models.CharField(max_length=255)
    description = models.TextField()
    work_type = models.CharField(max_length=50, choices=WORK_TYPE_CHOICES)

    file = models.FileField(upload_to='creative_works/',
                            validators=[validate_file_size])
    thumbnail = models.ImageField(
        upload_to='thumbnails/', blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    # Keep track of users who liked the work
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='liked_works', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate thumbnail if a file is uploaded but no thumbnail exists
        if self.file and not self.thumbnail:
            try:
                # Open the uploaded file using Pillow
                img = Image.open(self.file)

                # Convert to RGB to avoid issues with saving as JPEG (e.g., if original is PNG with transparency)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create the thumbnail (Pillow modifies the image in-place to max 400x400)
                img.thumbnail((400, 400))

                # Save the thumbnail to a BytesIO buffer
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)

                # Construct a new filename for the thumbnail
                filename = os.path.basename(self.file.name)
                name, _ = os.path.splitext(filename)
                thumb_filename = f"{name}_thumb.jpg"

                # Save the buffer content to the thumbnail field
                self.thumbnail.save(thumb_filename, ContentFile(
                    thumb_io.getvalue()), save=False)
            except Exception as e:
                # If it's not an image (e.g., PDF, audio) or corrupted, safely skip generation
                logging.getLogger(__name__).warning(
                    'Could not generate thumbnail for %s: %s', self.file.name, e)
            finally:
                # Reset the file pointer in case Django needs to read it again during the actual save
                if self.file and hasattr(self.file, 'seek'):
                    self.file.seek(0)

        super().save(*args, **kwargs)


class Collaboration(models.Model):
    """Collaboration request between artists or from clients"""
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaborations_initiated'
    )
    collaborator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collaborations_received'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=COLLABORATION_STATUS_CHOICES, default='pending')

    required_skills = models.TextField(
        blank=True, null=True, help_text="Comma-separated required skills")
    timeline = models.CharField(max_length=100, blank=True, null=True)
    budget_range = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.creator.username} → {self.collaborator.username}: {self.title}"


class Project(models.Model):
    """Project representing a collaborative work"""
    collaboration = models.OneToOneField(
        Collaboration, on_delete=models.CASCADE, related_name='project')

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=PROJECT_STATUS_CHOICES, default='draft')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='joined_projects')

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    deliverables = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPE_CHOICES = (
        ('collaboration_request', 'Collaboration Request'),
        ('collaboration_accepted', 'Collaboration Accepted'),
        ('collaboration_rejected', 'Collaboration Rejected'),
        ('project_update', 'Project Update'),
        ('message', 'Message'),
        ('profile_view', 'Profile View'),
        ('mentorship_request', 'Mentorship Request'),
        ('mentorship_accepted', 'Mentorship Accepted'),
        ('mentorship_rejected', 'Mentorship Rejected'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='sent_notifications', blank=True, null=True)

    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    # Reference to related objects (polymorphic-like behavior)
    related_collaboration = models.ForeignKey(
        Collaboration, on_delete=models.CASCADE, blank=True, null=True)
    related_project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True)
    related_mentorship = models.ForeignKey(
        'MentorshipRequest', on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    """Send an email to recipient when a new notification is created.
    """
    if not created:
        return

    try:
        recipient = instance.recipient
        if not recipient or not getattr(recipient, 'email', None):
            return

        recipient_email = recipient.email
        title = instance.title or 'Notification from The Creative Nexus'
        message = instance.message or ''
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL',
                             'sedemkofiamuzu@gmail.com')

        def send_email_async():
            try:
                send_mail(
                    title,
                    message,
                    from_email,
                    [recipient_email],
                    fail_silently=False
                )
            except Exception as e:
                logging.getLogger(__name__).exception(
                    'Failed to send notification email: %s', e)

        # Run in a background thread to prevent blocking the web request
        threading.Thread(target=send_email_async, daemon=True).start()
    except Exception as e:
        logging.getLogger(__name__).exception(
            'Error setting up notification email: %s', e)


class Rating(models.Model):
    """Rating system for collaborations"""
    collaboration = models.ForeignKey(
        Collaboration, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')

    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('collaboration', 'rater')

    def __str__(self):
        return f"{self.rater.username} rated {self.rated_user.username}: {self.rating}/5"


class MentorshipRequest(models.Model):
    """Mentorship request from junior creator to senior mentor"""
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentorship_requests_received'
    )
    mentee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentorship_requests_sent'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=MENTORSHIP_STATUS_CHOICES, default='pending')

    skills_to_learn = models.TextField(
        blank=True, null=True, help_text="Comma-separated skills mentee wants to learn")
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('mentor', 'mentee')

    def __str__(self):
        return f"{self.mentee.username} → {self.mentor.username}: {self.title}"


class AuditLog(models.Model):
    """Immutable record of system transactions and state changes"""
    ACTION_CHOICES = (
        ('status_change', 'Status Change'),
        ('approval', 'Approval'),
        ('rejection', 'Rejection'),
        ('creation', 'Creation'),
        ('other', 'Other'),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(
        max_length=50, help_text="Model name, e.g., Project, Collaboration")
    entity_id = models.PositiveIntegerField()
    details = models.TextField(help_text="JSON or text details of the change")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} performed {self.action} on {self.entity_type} {self.entity_id}"


@receiver(m2m_changed, sender=CreativeWork.liked_by.through)
def update_portfolio_likes(sender, instance, action, **kwargs):
    """
    Automatically update the work's like count and the portfolio's 
    total likes whenever a user likes or unlikes a creative work.
    """
    pk_set = kwargs.get('pk_set', set())

    if action == 'post_add':
        instance.likes += len(pk_set)
        instance.save(update_fields=['likes'])
    elif action == 'post_remove':
        instance.likes = max(0, instance.likes - len(pk_set))
        instance.save(update_fields=['likes'])
    elif action == 'post_clear':
        instance.likes = 0
        instance.save(update_fields=['likes'])

    if action in ['post_add', 'post_remove', 'post_clear']:
        # Update the portfolio's total likes
        if instance.portfolio:
            total = instance.portfolio.works.aggregate(
                total=Sum('likes'))['total'] or 0
            instance.portfolio.total_likes = total
            instance.portfolio.save(update_fields=['total_likes'])
