from rest_framework import serializers
from .models import Portfolio, CreativeWork, Collaboration, Project, Notification, Rating, MentorshipRequest


class CreativeWorkSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(
        source='creator.username', read_only=True)
    work_type_display = serializers.SerializerMethodField()

    class Meta:
        model = CreativeWork
        fields = (
            'id', 'creator', 'creator_username', 'title', 'description', 'work_type',
            'work_type_display', 'file', 'thumbnail', 'is_featured', 'views', 'likes', 'created_at'
        )
        read_only_fields = ('id', 'creator', 'views', 'likes', 'created_at')

    def get_work_type_display(self, obj):
        return obj.get_work_type_display()


class PortfolioSerializer(serializers.ModelSerializer):
    works = CreativeWorkSerializer(many=True, read_only=True)
    creator_username = serializers.CharField(
        source='creator.username', read_only=True)

    class Meta:
        model = Portfolio
        fields = (
            'id', 'creator', 'creator_username', 'title', 'description', 'featured_work',
            'works', 'total_views', 'total_likes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'creator', 'total_views',
                            'total_likes', 'created_at', 'updated_at')


class CollaborationListSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(
        source='creator.username', read_only=True)
    collaborator_username = serializers.CharField(
        source='collaborator.username', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = Collaboration
        fields = (
            'id', 'creator', 'creator_username', 'collaborator',
            'collaborator_username', 'title', 'description', 'status',
            'status_display', 'required_skills', 'timeline', 'budget_range',
            'created_at'
        )
        read_only_fields = ('id', 'creator', 'status', 'created_at')


class CollaborationDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(
        source='creator.username', read_only=True)
    collaborator_username = serializers.CharField(
        source='collaborator.username', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = Collaboration
        fields = (
            'id', 'creator', 'creator_username', 'collaborator', 'collaborator_username',
            'title', 'description', 'status', 'status_display', 'required_skills',
            'timeline', 'budget_range', 'created_at', 'updated_at', 'responded_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'responded_at')


class ProjectSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True)
    team_members_usernames = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'collaboration', 'title', 'description', 'status', 'status_display',
            'created_by', 'created_by_username', 'team_members', 'team_members_usernames',
            'start_date', 'end_date', 'deliverables', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_team_members_usernames(self, obj):
        return [member.username for member in obj.team_members.all()]


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
        source='sender.username', read_only=True, allow_null=True)
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'sender', 'sender_username', 'notification_type',
            'notification_type_display', 'title', 'message', 'is_read', 'read_at',
            'related_collaboration', 'related_project', 'created_at'
        )
        read_only_fields = ('id', 'recipient', 'created_at', 'read_at')


class RatingSerializer(serializers.ModelSerializer):
    rater_username = serializers.CharField(
        source='rater.username', read_only=True)
    rated_user_username = serializers.CharField(
        source='rated_user.username', read_only=True)

    class Meta:
        model = Rating
        fields = (
            'id', 'collaboration', 'rater', 'rater_username', 'rated_user',
            'rated_user_username', 'rating', 'review', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class MentorshipRequestListSerializer(serializers.ModelSerializer):
    mentor_username = serializers.CharField(
        source='mentor.username', read_only=True)
    mentee_username = serializers.CharField(
        source='mentee.username', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = MentorshipRequest
        fields = (
            'id', 'mentor', 'mentor_username', 'mentee',
            'mentee_username', 'title', 'description', 'status',
            'status_display', 'skills_to_learn', 'experience_level',
            'created_at'
        )
        read_only_fields = ('id', 'mentee', 'status', 'created_at')


class MentorshipRequestDetailSerializer(serializers.ModelSerializer):
    mentor_username = serializers.CharField(
        source='mentor.username', read_only=True)
    mentee_username = serializers.CharField(
        source='mentee.username', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = MentorshipRequest
        fields = (
            'id', 'mentor', 'mentor_username', 'mentee', 'mentee_username',
            'title', 'description', 'status', 'status_display', 'skills_to_learn',
            'experience_level', 'created_at', 'updated_at', 'responded_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'responded_at')
