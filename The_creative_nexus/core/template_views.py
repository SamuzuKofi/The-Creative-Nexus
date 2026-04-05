from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from accounts.models import CustomUser, UserProfile
from core.models import Portfolio, CreativeWork, Collaboration, Project, Notification, MentorshipRequest
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F, Exists, OuterRef
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def home(request):
    """Home page with gallery preview"""
    works = CreativeWork.objects.select_related('creator').all()[:12]
    return render(request, 'core/home.html', {'works': works})


@login_required(login_url='login')
def dashboard(request):
    """User dashboard"""
    user = request.user
    # Ensure user has a profile
    profile, _ = UserProfile.objects.get_or_create(user=user)

    try:
        portfolio = Portfolio.objects.get(creator=user)
    except Portfolio.DoesNotExist:
        portfolio = None

    my_works = CreativeWork.objects.filter(creator=user)
    collaborations = (Collaboration.objects.filter(creator=user) |
                      Collaboration.objects.filter(collaborator=user)).select_related('creator', 'collaborator')

    unread_notifications = Notification.objects.filter(
        recipient=user, is_read=False).select_related('sender')

    mentorship_requests = (MentorshipRequest.objects.filter(mentor=user) |
                           MentorshipRequest.objects.filter(mentee=user)).select_related('mentor', 'mentee')

    context = {
        'portfolio': portfolio,
        'my_works': my_works,
        'collaborations': collaborations,
        'unread_notifications': unread_notifications,
        'mentorship_requests': mentorship_requests
    }
    return render(request, 'core/dashboard.html', context)


@login_required(login_url='login')
def portfolio_view(request, user_id=None):
    """View and manage portfolio"""
    # Helper function to get creator skills list
    def get_skills_list(user):
        # Ensure user has a profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.skills:
            # Try splitting by comma first, then pipe (matching explore_view logic)
            if ',' in profile.skills:
                return [s.strip() for s in profile.skills.split(',')]
            elif '|' in profile.skills:
                return [s.strip() for s in profile.skills.split('|')]
            else:
                return [profile.skills.strip()]
        return []

    # If user_id is provided, view someone else's portfolio
    if user_id:
        from django.contrib.auth import get_user_model
        from django.http import Http404

        User = get_user_model()

        # Check if user exists
        try:
            portfolio_owner = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")

        # Try to get portfolio
        portfolio = Portfolio.objects.filter(creator=portfolio_owner).first()

        if not portfolio:
            # Return empty portfolio view for user without portfolio
            context = {
                'portfolio': None,
                'works': [],
                'is_own_portfolio': portfolio_owner == request.user,
                'creator_skills': get_skills_list(portfolio_owner),
                'portfolio_owner': portfolio_owner
            }
            return render(request, 'core/portfolio.html', context)

        works_qs = portfolio.works.all()
        if request.user.is_authenticated:
            liked_subquery = CreativeWork.objects.filter(
                pk=OuterRef('pk'), liked_by=request.user.pk)
            works = works_qs.annotate(is_liked_by_user=Exists(liked_subquery))
        else:
            works = works_qs

        # Increment portfolio view count when someone (not the owner) visits
        try:
            if request.user != portfolio_owner:
                Portfolio.objects.filter(pk=portfolio.pk).update(
                    total_views=F('total_views') + 1)
                # Create a notification for authenticated viewers
                if request.user.is_authenticated:
                    Notification.objects.create(
                        recipient=portfolio_owner,
                        sender=request.user,
                        notification_type='profile_view',
                        title=f'{request.user.username} viewed your portfolio',
                        message=f'{request.user.username} viewed your portfolio: {portfolio.title}'
                    )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                'Failed to update portfolio view count or send notification: %s', e)
            # Don't fail page render if counting a view fails
            pass
        context = {
            'portfolio': portfolio,
            'works': works,
            'is_own_portfolio': portfolio_owner == request.user,
            'creator_skills': get_skills_list(portfolio_owner)
        }
        return render(request, 'core/portfolio.html', context)

    # Otherwise, view/manage own portfolio
    user = request.user
    try:
        portfolio = Portfolio.objects.get(creator=user)
    except Portfolio.DoesNotExist:
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category', 'other')
            cover_image = request.FILES.get('cover_image')

            portfolio = Portfolio.objects.create(
                creator=user,
                title=title,
                description=description,
                category=category,
                cover_image=cover_image
            )
            messages.success(request, 'Portfolio created successfully!')
            return redirect('portfolio')
        else:
            context = {
                'portfolio': None,
                'works': [],
                'is_own_portfolio': True,
                'creator_skills': get_skills_list(user)
            }
            return render(request, 'core/portfolio.html', context)

    works_qs = portfolio.works.all()
    liked_subquery = CreativeWork.objects.filter(
        pk=OuterRef('pk'), liked_by=request.user.pk)
    works = works_qs.annotate(is_liked_by_user=Exists(liked_subquery))

    context = {
        'portfolio': portfolio,
        'works': works,
        'is_own_portfolio': True,
        'creator_skills': get_skills_list(user)
    }
    return render(request, 'core/portfolio.html', context)


@login_required(login_url='login')
def profile_view(request):
    """View and edit user profile"""
    user = request.user
    # Ensure user has a profile
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.website = request.POST.get('website', profile.website)
        profile.skills = request.POST.get('skills', profile.skills)
        profile.years_experience = request.POST.get(
            'years_experience', profile.years_experience)

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {'profile': profile, 'user': user}
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def collaborations_view(request):
    """View collaborations"""
    user = request.user
    sent = Collaboration.objects.filter(
        creator=user).select_related('collaborator')
    received = Collaboration.objects.filter(
        collaborator=user).select_related('creator')

    context = {'sent': sent, 'received': received}
    return render(request, 'core/collaborations.html', context)


@login_required(login_url='login')
def explore_view(request):
    """Explore creators and their portfolios"""
    role = request.GET.get('role')
    search = request.GET.get('search')

    profiles = UserProfile.objects.exclude(
        user=request.user).select_related('user')

    if role:
        profiles = profiles.filter(role=role)

    if search:
        from django.db.models import Q
        profiles = profiles.filter(
            Q(user__username__icontains=search) |
            Q(skills__icontains=search) |
            Q(location__icontains=search)
        )

    # Process skills for each profile to avoid template syntax issues
    profiles_with_skills = []
    for profile in profiles:
        skills_list = []
        if profile.skills:
            # Try splitting by comma first, then pipe
            if ',' in profile.skills:
                skills_list = [s.strip() for s in profile.skills.split(',')]
            elif '|' in profile.skills:
                skills_list = [s.strip() for s in profile.skills.split('|')]
            else:
                skills_list = [profile.skills.strip()]
        profile.skills_list = skills_list
        profiles_with_skills.append(profile)

    context = {'profiles': profiles_with_skills,
               'selected_role': role, 'search': search}
    return render(request, 'core/explore.html', context)


def register_view(request):
    """Registration page (API-driven)"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/register.html')


@login_required(login_url='login')
def notifications_view(request):
    """Notification center page for the user"""
    user = request.user
    notifications = Notification.objects.filter(
        recipient=user).order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'core/notifications.html', context)


@login_required(login_url='login')
def projects_view(request):
    """List projects for current user and quick actions"""
    user = request.user
    projects = Project.objects.filter(
        Q(created_by=user) | Q(team_members=user)
    ).select_related('created_by').prefetch_related('team_members').distinct()
    context = {'projects': projects}
    return render(request, 'core/projects.html', context)


@login_required(login_url='login')
def project_detail(request, project_id):
    """Detailed project view with status updates and member management"""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        from django.http import Http404
        raise Http404('Project not found')

    # Ensure user can view the project
    user = request.user
    if not (project.created_by == user or user in project.team_members.all()):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('You do not have access to this project')

    context = {'project': project}
    return render(request, 'core/project_detail.html', context)


def login_view(request):
    """Login page (API-driven)"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def verify_email_view(request):
    """Email verification page"""
    token = request.GET.get('token')

    if not token:
        return render(request, 'accounts/verify_email.html', {
            'success': False,
            'message': 'No verification token provided.'
        })

    try:
        user = CustomUser.objects.get(email_verification_token=token)
        user.email_verified = True
        user.email_verification_token = ''
        user.save()

        return render(request, 'accounts/verify_email.html', {
            'success': True,
            'message': 'Email verified successfully! You can now login.',
            'user_email': user.email
        })
    except CustomUser.DoesNotExist:
        return render(request, 'accounts/verify_email.html', {
            'success': False,
            'message': 'Invalid or expired verification token. Please register again.'
        })
