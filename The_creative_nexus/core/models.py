from django.db import models
from django.conf import settings
from django.utils import timezone

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

    total_views = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)

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

    file = models.FileField(upload_to='creative_works/')
    thumbnail = models.ImageField(
        upload_to='thumbnails/', blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


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
