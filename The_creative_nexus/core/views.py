from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from .models import Portfolio, CreativeWork, Collaboration, Project, Notification, Rating, MentorshipRequest
from .serializers import (
    PortfolioSerializer,
    CreativeWorkSerializer,
    CollaborationListSerializer,
    CollaborationDetailSerializer,
    ProjectSerializer,
    NotificationSerializer,
    RatingSerializer,
    MentorshipRequestListSerializer,
    MentorshipRequestDetailSerializer
)


class PortfolioViewSet(viewsets.ModelViewSet):
    """Portfolio management"""
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Portfolio.objects.all().select_related('creator')

    def create(self, request, *args, **kwargs):
        """Create portfolio for current user"""
        request.data['creator'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_portfolio(self, request):
        """Get current user's portfolio"""
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            portfolio = Portfolio.objects.get(creator=request.user)
            serializer = self.get_serializer(portfolio)
            return Response(serializer.data)
        except Portfolio.DoesNotExist:
            return Response({'error': 'Portfolio not found'}, status=status.HTTP_404_NOT_FOUND)


class CreativeWorkViewSet(viewsets.ModelViewSet):
    """Creative work (asset) management"""
    queryset = CreativeWork.objects.all()
    serializer_class = CreativeWorkSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CreativeWork.objects.all().select_related('creator', 'portfolio')

    def perform_create(self, serializer):
        """Assign creator and portfolio on creation"""
        # Get or create user's portfolio
        try:
            portfolio = Portfolio.objects.get(creator=self.request.user)
        except Portfolio.DoesNotExist:
            # If no portfolio exists, create one with default values
            portfolio = Portfolio.objects.create(
                creator=self.request.user,
                title=f"{self.request.user.username}'s Portfolio",
                description="My creative works collection"
            )

        serializer.save(creator=self.request.user, portfolio=portfolio)

    @action(detail=False, methods=['get'])
    def my_works(self, request):
        """Get current user's creative works"""
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        works = CreativeWork.objects.filter(creator=request.user)
        serializer = self.get_serializer(works, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a creative work"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required to like a work.'}, status=status.HTTP_401_UNAUTHORIZED)

        work = self.get_object()

        if request.user in work.liked_by.all():
            # User has already liked it, so "unlike"
            work.liked_by.remove(request.user)
            is_liked = False
        else:
            # User has not liked it yet, so "like"
            work.liked_by.add(request.user)
            is_liked = True

        # The signal automatically updates counts, we just need to refresh our instance
        work.refresh_from_db()
        return Response({'likes': work.likes, 'is_liked': is_liked})

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Record a view on creative work"""
        work = self.get_object()
        work.views += 1
        work.save()
        return Response({'views': work.views})


class CollaborationViewSet(viewsets.ModelViewSet):
    """Collaboration request management"""
    queryset = Collaboration.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Collaboration.objects.filter(
            Q(creator=user) | Q(collaborator=user)
        ).select_related('creator', 'collaborator')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollaborationDetailSerializer
        return CollaborationListSerializer

    def perform_create(self, serializer):
        """Create collaboration request"""
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a collaboration request"""
        collaboration = self.get_object()
        if collaboration.collaborator != request.user:
            return Response(
                {'error': 'Only the collaborator can accept'},
                status=status.HTTP_403_FORBIDDEN
            )

        collaboration.status = 'accepted'
        collaboration.responded_at = timezone.now()
        collaboration.save()

        # Create notification
        Notification.objects.create(
            recipient=collaboration.creator,
            sender=request.user,
            notification_type='collaboration_accepted',
            title=f'{request.user.username} accepted your collaboration request',
            message=f'Good news! {request.user.username} has accepted your collaboration request for {collaboration.title}',
            related_collaboration=collaboration
        )

        # Create project
        Project.objects.create(
            collaboration=collaboration,
            title=collaboration.title,
            description=collaboration.description,
            created_by=collaboration.creator,
        )

        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a collaboration request"""
        collaboration = self.get_object()
        if collaboration.collaborator != request.user:
            return Response(
                {'error': 'Only the collaborator can reject'},
                status=status.HTTP_403_FORBIDDEN
            )

        collaboration.status = 'rejected'
        collaboration.responded_at = timezone.now()
        collaboration.save()

        # Create notification
        Notification.objects.create(
            recipient=collaboration.creator,
            sender=request.user,
            notification_type='collaboration_rejected',
            title=f'{request.user.username} rejected your collaboration request',
            message=f'{request.user.username} has declined your collaboration request for {collaboration.title}',
            related_collaboration=collaboration
        )

        return Response({'status': 'rejected'})


class ProjectViewSet(viewsets.ModelViewSet):
    """Project management"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(created_by=user) | Q(team_members=user)
        ).select_related('created_by').prefetch_related('team_members')

    def perform_create(self, serializer):
        """Create project"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add team member to project"""
        project = self.get_object()
        if project.created_by != request.user:
            return Response(
                {'error': 'Only the creator can add members'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            project.team_members.add(user)
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update project status"""
        project = self.get_object()
        if project.created_by != request.user:
            return Response(
                {'error': 'Only the creator can update status'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if new_status not in dict([(choice[0], choice[0]) for choice in Project._meta.get_field('status').choices]):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        project.status = new_status
        project.save()

        # Notify team members
        for member in project.team_members.all():
            Notification.objects.create(
                recipient=member,
                sender=request.user,
                notification_type='project_update',
                title=f'Project status updated: {new_status}',
                message=f'{request.user.username} updated {project.title} status to {new_status}',
                related_project=project
            )

        return Response(ProjectSerializer(project).data)


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class RatingViewSet(viewsets.ModelViewSet):
    """Rating management"""
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create rating"""
        serializer.save(rater=self.request.user)

    @action(detail=False, methods=['get'])
    def user_ratings(self, request):
        """Get ratings for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)

        ratings = Rating.objects.filter(rated_user_id=user_id)
        serializer = self.get_serializer(ratings, many=True)
        average = sum(r.rating for r in ratings) / \
            len(ratings) if ratings else 0
        return Response({
            'ratings': serializer.data,
            'average_rating': round(average, 2),
            'total_ratings': len(ratings)
        })


class MentorshipRequestViewSet(viewsets.ModelViewSet):
    """Mentorship request management"""
    queryset = MentorshipRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MentorshipRequest.objects.filter(
            Q(mentor=user) | Q(mentee=user)
        ).select_related('mentor', 'mentee')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MentorshipRequestDetailSerializer
        return MentorshipRequestListSerializer

    def perform_create(self, serializer):
        """Create mentorship request"""
        serializer.save(mentee=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a mentorship request"""
        mentorship = self.get_object()
        if mentorship.mentor != request.user:
            return Response(
                {'error': 'Only the mentor can accept'},
                status=status.HTTP_403_FORBIDDEN
            )

        mentorship.status = 'accepted'
        mentorship.responded_at = timezone.now()
        mentorship.save()

        # Create notification
        Notification.objects.create(
            recipient=mentorship.mentee,
            sender=request.user,
            notification_type='mentorship_accepted',
            title=f'{request.user.username} accepted your mentorship request',
            message=f'Great! {request.user.username} has accepted your mentorship request: {mentorship.title}',
            related_mentorship=mentorship
        )

        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a mentorship request"""
        mentorship = self.get_object()
        if mentorship.mentor != request.user:
            return Response(
                {'error': 'Only the mentor can reject'},
                status=status.HTTP_403_FORBIDDEN
            )

        mentorship.status = 'rejected'
        mentorship.responded_at = timezone.now()
        mentorship.save()

        # Create notification
        Notification.objects.create(
            recipient=mentorship.mentee,
            sender=request.user,
            notification_type='mentorship_rejected',
            title=f'{request.user.username} declined your mentorship request',
            message=f'{request.user.username} was unable to accept your mentorship request: {mentorship.title}',
            related_mentorship=mentorship
        )

        return Response({'status': 'rejected'})

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get mentorship requests sent by current user"""
        requests = MentorshipRequest.objects.filter(mentee=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received_requests(self, request):
        """Get mentorship requests received by current user"""
        requests = MentorshipRequest.objects.filter(mentor=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
