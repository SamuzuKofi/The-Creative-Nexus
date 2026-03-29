from django.contrib import admin
from .models import Portfolio, CreativeWork, Collaboration, Project, Notification, Rating, MentorshipRequest, AuditLog


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title', 'total_views',
                    'total_likes', 'created_at')
    search_fields = ('creator__email', 'title')
    readonly_fields = ('total_views', 'total_likes',
                       'created_at', 'updated_at')


@admin.register(CreativeWork)
class CreativeWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'work_type',
                    'is_featured', 'views', 'likes', 'created_at')
    list_filter = ('work_type', 'is_featured', 'created_at')
    search_fields = ('title', 'creator__email', 'description')
    readonly_fields = ('views', 'likes', 'created_at', 'updated_at')


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'collaborator', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'creator__email', 'collaborator__email')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status',
                    'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'created_by__email', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type',
                    'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'recipient__email', 'message')
    readonly_fields = ('created_at', 'read_at')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rated_user', 'rater', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('rated_user__email', 'rater__email')


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'mentor', 'mentee', 'status',
                    'experience_level', 'created_at')
    list_filter = ('status', 'experience_level', 'created_at')
    search_fields = ('title', 'mentor__email', 'mentee__email', 'description')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'entity_type',
                    'entity_id', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('actor__email', 'actor__username', 'details')
    readonly_fields = ('actor', 'action', 'entity_type',
                       'entity_id', 'details', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        # Audit logs should be immutable, not created manually
        return False
