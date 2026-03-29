"""
Integration tests for template views to ensure all user-facing features work correctly
Tests cover:
1. Featured works links point to creator's portfolio
2. Portfolio viewing for users without portfolios
3. Profile access and creation
4. Explore page search and filters
5. Dashboard profile access
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from core.models import Portfolio, CreativeWork

User = get_user_model()


class FeaturedWorksTestCase(TestCase):
    """Test featured works section in home and dashboard"""

    def setUp(self):
        """Create test users, portfolios and works"""
        self.client = Client()
        
        # Create a creator
        self.creator = User.objects.create_user(
            username='creator_user',
            email='creator@test.com',
            password='testpass123'
        )
        
        # Ensure profile exists
        self.profile = UserProfile.objects.get_or_create(user=self.creator)[0]
        self.profile.role = 'creator'
        self.profile.save()
        
        # Create portfolio
        self.portfolio = Portfolio.objects.create(
            creator=self.creator,
            title='Test Portfolio',
            description='A test portfolio'
        )
        
        # Create a creative work
        self.work = CreativeWork.objects.create(
            creator=self.creator,
            portfolio=self.portfolio,
            title='Test Work',
            description='Test work description',
            work_type='digital_art'
        )

    def test_home_page_featured_works_url(self):
        """Test that featured works link to creator's portfolio, not user's own"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains a link to the creator's portfolio
        # The URL should be /portfolio/<creator_id>/ not /portfolio/
        self.assertContains(
            response,
            f'href="/portfolio/{self.creator.id}/"',
            html=False
        )

    def test_featured_works_visible_without_authentication(self):
        """Test that featured works are visible to unauthenticated users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.work.title)
        self.assertContains(response, self.creator.username)

    def test_featured_works_visible_with_authentication(self):
        """Test that featured works are visible to authenticated users"""
        self.client.login(username='creator_user', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.work.title)


class PortfolioViewTestCase(TestCase):
    """Test portfolio viewing functionality"""

    def setUp(self):
        """Create test users and portfolios"""
        self.client = Client()
        
        # Create viewer (logged-in user)
        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@test.com',
            password='testpass123'
        )
        UserProfile.objects.get_or_create(user=self.viewer)
        
        # Create portfolio owner
        self.portfolio_owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        UserProfile.objects.get_or_create(user=self.portfolio_owner)
        
        # Create user without portfolio
        self.no_portfolio_user = User.objects.create_user(
            username='no_portfolio',
            email='no_portfolio@test.com',
            password='testpass123'
        )
        UserProfile.objects.get_or_create(user=self.no_portfolio_user)
        
        # Create portfolio for owner
        self.portfolio = Portfolio.objects.create(
            creator=self.portfolio_owner,
            title='Owner Portfolio',
            description='Owners portfolio'
        )

    def test_view_own_portfolio(self):
        """Test user can access their own portfolio"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('portfolio'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.portfolio.title)

    def test_view_other_user_portfolio(self):
        """Test user can view another user's portfolio"""
        self.client.login(username='viewer', password='testpass123')
        response = self.client.get(
            reverse('view-portfolio', args=[self.portfolio_owner.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.portfolio.title)

    def test_view_portfolio_no_portfolio_created(self):
        """Test viewing portfolio for user without portfolio"""
        self.client.login(username='no_portfolio', password='testpass123')
        response = self.client.get(reverse('portfolio'))
        # Should not error, should show empty portfolio state
        self.assertEqual(response.status_code, 200)

    def test_view_other_user_without_portfolio(self):
        """Test viewing profile of user without portfolio"""
        self.client.login(username='viewer', password='testpass123')
        response = self.client.get(
            reverse('view-portfolio', args=[self.no_portfolio_user.id])
        )
        # Should not error, should show empty state
        self.assertEqual(response.status_code, 200)

    def test_portfolio_creation_form_available(self):
        """Test that portfolio creation form loads without error"""
        self.client.login(username='no_portfolio', password='testpass123')
        response = self.client.get(reverse('portfolio'))
        self.assertEqual(response.status_code, 200)
        # Should have form available since no portfolio exists
        self.assertIn('portfolio', response.context)

    def test_profile_always_exists_for_portfolio_view(self):
        """Test that accessing portfolio creates profile if missing"""
        # Create a new user
        new_user = User.objects.create_user(
            username='new_user',
            email='new@test.com',
            password='testpass123'
        )
        # Django signals should have auto-created the profile
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertIsNotNone(new_user.profile)
        
        # Login and access portfolio
        self.client.login(username='new_user', password='testpass123')
        response = self.client.get(reverse('portfolio'))
        
        # Should succeed without RelatedObjectDoesNotExist error
        self.assertEqual(response.status_code, 200)


class ProfileViewTestCase(TestCase):
    """Test profile viewing and editing"""

    def setUp(self):
        """Create test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='profile_user',
            email='profile@test.com',
            password='testpass123'
        )
        # Ensure profile exists
        self.profile = UserProfile.objects.get_or_create(user=self.user)[0]

    def test_profile_view_accessible(self):
        """Test profile view is accessible"""
        self.client.login(username='profile_user', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        # Check for profile form elements
        self.assertContains(response, 'bio', html=False)
        self.assertContains(response, 'location', html=False)

    def test_profile_view_creates_profile_if_missing(self):
        """Test that profile view creates profile if missing"""
        # Create user without profile
        new_user = User.objects.create_user(
            username='new_profile_user',
            email='newprofile@test.com',
            password='testpass123'
        )
        # Don't create profile
        if hasattr(new_user, 'profile'):
            # Django signals should have created it, but let's test anyway
            pass
        
        self.client.login(username='new_profile_user', password='testpass123')
        response = self.client.get(reverse('profile'))
        
        # Should not error
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_saves_data(self):
        """Test that profile can be edited and saved"""
        self.client.login(username='profile_user', password='testpass123')
        
        response = self.client.post(
            reverse('profile'),
            {
                'bio': 'Updated bio',
                'location': 'Accra, Ghana',
                'skills': 'Python, Django, React',
                'years_experience': '5'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify data was saved
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.location, 'Accra, Ghana')


class DashboardTestCase(TestCase):
    """Test dashboard functionality"""

    def setUp(self):
        """Create test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashboard_user',
            email='dashboard@test.com',
            password='testpass123'
        )
        # Ensure profile exists
        self.profile = UserProfile.objects.get_or_create(user=self.user)[0]

    def test_dashboard_accessible(self):
        """Test dashboard is accessible for authenticated users"""
        self.client.login(username='dashboard_user', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login/', response.url)

    def test_dashboard_profile_accessible(self):
        """Test that dashboard can access user profile without error"""
        self.client.login(username='dashboard_user', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Should not error with RelatedObjectDoesNotExist
        self.assertEqual(response.status_code, 200)
        # Should contain profile role display
        self.assertContains(response, 'Creator')  # default role

    def test_dashboard_shows_profile_picture_safely(self):
        """Test dashboard handles missing profile picture gracefully"""
        self.client.login(username='dashboard_user', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Should show either picture or icon without error
        self.assertEqual(response.status_code, 200)


class ExploreViewTestCase(TestCase):
    """Test explore page and search functionality"""

    def setUp(self):
        """Create test data"""
        self.client = Client()
        
        # Create current user
        self.current_user = User.objects.create_user(
            username='explorer',
            email='explorer@test.com',
            password='testpass123'
        )
        UserProfile.objects.get_or_create(user=self.current_user)
        
        # Create creators with different skills
        self.creator1 = User.objects.create_user(
            username='graphic_designer',
            email='designer@test.com',
            password='testpass123'
        )
        profile1 = UserProfile.objects.get_or_create(user=self.creator1)[0]
        profile1.role = 'creator'
        profile1.skills = 'Graphic Design, UI/UX'
        profile1.location = 'Accra'
        profile1.bio = 'Professional graphic designer'
        profile1.save()
        
        self.creator2 = User.objects.create_user(
            username='photographer',
            email='photographer@test.com',
            password='testpass123'
        )
        profile2 = UserProfile.objects.get_or_create(user=self.creator2)[0]
        profile2.role = 'creator'
        profile2.skills = 'Photography, Videography'
        profile2.location = 'Kumasi'
        profile2.bio = 'Event photographer'
        profile2.save()
        
        # Create a mentor
        self.mentor = User.objects.create_user(
            username='mentor_user',
            email='mentor@test.com',
            password='testpass123'
        )
        mentor_profile = UserProfile.objects.get_or_create(user=self.mentor)[0]
        mentor_profile.role = 'mentor'
        mentor_profile.skills = 'Teaching, Mentoring'
        mentor_profile.save()

    def test_explore_page_loads(self):
        """Test explore page loads successfully"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'))
        self.assertEqual(response.status_code, 200)

    def test_explore_shows_all_creators_by_default(self):
        """Test explore shows all creators by default (except current user)"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'))
        
        self.assertEqual(response.status_code, 200)
        # Should show both creators
        self.assertContains(response, 'graphic_designer')
        self.assertContains(response, 'photographer')
        self.assertContains(response, 'mentor_user')

    def test_search_by_username(self):
        """Test searching creators by username"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'), {'search': 'photographer'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'photographer')
        # Should not contain the other creator
        self.assertNotContains(response, 'graphic_designer')

    def test_search_by_skills(self):
        """Test searching creators by skills"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'), {'search': 'Photography'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'photographer')

    def test_search_by_location(self):
        """Test searching creators by location"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'), {'search': 'Accra'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'graphic_designer')

    def test_filter_by_role(self):
        """Test filtering creators by role"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'), {'role': 'mentor'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'mentor_user')
        # Should not show creators
        self.assertNotContains(response, 'graphic_designer')

    def test_search_and_filter_combined(self):
        """Test searching and filtering together"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(
            reverse('explore'),
            {'search': 'Accra', 'role': 'creator'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'graphic_designer')
        self.assertNotContains(response, 'photographer')

    def test_search_returns_empty_when_no_match(self):
        """Test search returns empty results gracefully"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'), {'search': 'nonexistent'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No creators found')

    def test_portfolio_link_from_explore(self):
        """Test that portfolio links in explore page work"""
        self.client.login(username='explorer', password='testpass123')
        response = self.client.get(reverse('explore'))
        
        # Should have links to view portfolios
        self.assertContains(
            response,
            f'href="/portfolio/{self.creator1.id}/"',
            html=False
        )


class ProfileCreationSignalTestCase(TestCase):
    """Test that UserProfile is automatically created for new users"""

    def test_profile_auto_created_on_user_creation(self):
        """Test that creating a user automatically creates a profile"""
        new_user = User.objects.create_user(
            username='signal_test',
            email='signal@test.com',
            password='testpass123'
        )
        
        # Profile should be auto-created by signal
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertIsNotNone(new_user.profile)
        self.assertEqual(new_user.profile.role, 'creator')  # default role
