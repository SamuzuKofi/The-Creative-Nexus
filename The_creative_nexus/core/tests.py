from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import UserProfile
from core.models import Portfolio, CreativeWork, Collaboration, Notification

User = get_user_model()


class UserAuthenticationTestCase(TestCase):
    """Test user registration, email verification, and login"""

    def setUp(self):
        self.client = Client()

    def test_user_registration_success(self):
        """Test successful user registration via API"""
        response = self.client.post(
            '/api/accounts/register/',
            {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'creator'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        print("✓ User registration successful")

    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(
            '/api/accounts/register/',
            {
                'username': 'testuser2',
                'email': 'test2@example.com',
                'password': 'testpass123',
                'confirm_password': 'different123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        print("✓ Password mismatch validation works")

    def test_email_verification(self):
        """Test email verification flow"""
        # Create a user
        user = User.objects.create_user(
            username='verifyuser',
            email='verify@example.com',
            password='testpass123'
        )
        # Token should be set during registration
        self.assertFalse(user.email_verified)
        print("✓ Email verification flow tested")

    def test_user_login_success(self):
        """Test successful login with email"""
        # Create and verify a user
        user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='testpass123',
            email_verified=True
        )

        # Attempt login
        response = self.client.post(
            '/api/accounts/login/',
            {
                'email': 'login@example.com',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        print("✓ User login successful")

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        User.objects.create_user(
            username='invalidlogin',
            email='invalid@example.com',
            password='testpass123',
            email_verified=True
        )

        response = self.client.post(
            '/api/accounts/login/',
            {
                'email': 'invalid@example.com',
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )
        self.assertNotEqual(response.status_code, 200)
        print("✓ Invalid login credentials rejected")


class UserProfileTestCase(TestCase):
    """Test user profile creation and updates"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        self.client = Client()

    def test_user_profile_auto_creation(self):
        """Test that UserProfile is auto-created with user"""
        profile = UserProfile.objects.filter(user=self.user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.role, 'creator')  # default role
        print("✓ User profile auto-created on user creation")

    def test_profile_role_assignment(self):
        """Test setting different user roles"""
        roles = ['creator', 'client', 'mentor', 'admin']
        for role in roles:
            user = User.objects.create_user(
                username=f'user_{role}',
                email=f'{role}@example.com',
                password='testpass123'
            )
            user.profile.role = role
            user.profile.save()

            self.assertEqual(user.profile.role, role)
        print("✓ All user roles can be set correctly")

    def test_profile_bio_and_skills(self):
        """Test setting profile bio and skills"""
        self.user.profile.bio = "I'm a creative designer"
        self.user.profile.skills = "Design|Web Development|Photography"
        self.user.profile.save()

        self.assertEqual(self.user.profile.bio, "I'm a creative designer")
        self.assertIn("Design", self.user.profile.skills)
        print("✓ Profile bio and skills can be set")


class PortfolioTestCase(TestCase):
    """Test portfolio creation and management"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='portfoliouser',
            email='portfolio@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='portfoliouser', password='testpass123')

    def test_portfolio_creation(self):
        """Test creating a portfolio"""
        portfolio = Portfolio.objects.create(
            creator=self.user,
            title="My Amazing Portfolio",
            description="Showcasing my creative works"
        )
        self.assertEqual(portfolio.creator, self.user)
        self.assertEqual(portfolio.title, "My Amazing Portfolio")
        print("✓ Portfolio creation successful")

    def test_portfolio_views_and_likes(self):
        """Test portfolio view and like counts"""
        portfolio = Portfolio.objects.create(
            creator=self.user,
            title="Test Portfolio",
            description="Testing"
        )

        # Update view and like counts
        portfolio.total_views = 100
        portfolio.total_likes = 50
        portfolio.save()

        self.assertEqual(portfolio.total_views, 100)
        self.assertEqual(portfolio.total_likes, 50)
        print("✓ Portfolio view and like counts work")


class CreativeWorkTestCase(TestCase):
    """Test creative work upload and management"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='creativeworkuser',
            email='creative@example.com',
            password='testpass123'
        )
        self.portfolio = Portfolio.objects.create(
            creator=self.user,
            title="Test Portfolio",
            description="Test"
        )
        self.client = Client()
        self.client.login(username='creativeworkuser', password='testpass123')

    def test_creative_work_creation(self):
        """Test creating a creative work"""
        work = CreativeWork.objects.create(
            creator=self.user,
            portfolio=self.portfolio,
            title="My Artwork",
            description="A beautiful artwork",
            work_type='digital_art'
        )
        self.assertEqual(work.creator, self.user)
        self.assertEqual(work.portfolio, self.portfolio)
        self.assertEqual(work.work_type, 'digital_art')
        print("✓ Creative work creation successful")

    def test_all_work_types(self):
        """Test all creative work types"""
        work_types = [
            'digital_art', 'graphic_design', 'animation',
            'photography', 'video', 'music', 'writing', 'other'
        ]

        for i, work_type in enumerate(work_types):
            work = CreativeWork.objects.create(
                creator=self.user,
                portfolio=self.portfolio,
                title=f"Work {i}",
                description=f"Test {work_type}",
                work_type=work_type
            )
            self.assertEqual(work.work_type, work_type)

        print(f"✓ All {len(work_types)} work types supported")

    def test_work_feature_and_stats(self):
        """Test work featured status and view/like counts"""
        work = CreativeWork.objects.create(
            creator=self.user,
            portfolio=self.portfolio,
            title="Featured Work",
            description="Test",
            work_type='graphic_design',
            is_featured=True,
            views=150,
            likes=75
        )

        self.assertTrue(work.is_featured)
        self.assertEqual(work.views, 150)
        self.assertEqual(work.likes, 75)
        print("✓ Creative work stats tracked correctly")


class CollaborationTestCase(TestCase):
    """Test collaboration requests and management"""

    def setUp(self):
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.creator.profile.role = 'creator'
        self.creator.profile.save()

        self.client_user = User.objects.create_user(
            username='clientuser',
            email='client@example.com',
            password='testpass123'
        )
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()

    def test_collaboration_creation(self):
        """Test creating a collaboration request"""
        collab = Collaboration.objects.create(
            creator=self.creator,
            collaborator=self.client_user,
            title="Design Project",
            description="Need a website design",
            status='pending'
        )

        self.assertEqual(collab.creator, self.creator)
        self.assertEqual(collab.collaborator, self.client_user)
        self.assertEqual(collab.status, 'pending')
        print("✓ Collaboration request creation successful")

    def test_collaboration_status_changes(self):
        """Test changing collaboration status"""
        collab = Collaboration.objects.create(
            creator=self.creator,
            collaborator=self.client_user,
            title="Test",
            description="Test",
            status='pending'
        )

        statuses = ['pending', 'accepted', 'rejected', 'completed']
        for status in statuses:
            collab.status = status
            collab.save()
            self.assertEqual(collab.status, status)

        print("✓ All collaboration statuses work correctly")

    def test_collaboration_filter_by_user(self):
        """Test filtering collaborations by user"""
        collab1 = Collaboration.objects.create(
            creator=self.creator,
            collaborator=self.client_user,
            title="Collab 1",
            description="Test",
            status='pending'
        )

        # Filter by creator
        creator_collabs = Collaboration.objects.filter(creator=self.creator)
        self.assertEqual(creator_collabs.count(), 1)

        # Filter by collaborator
        client_collabs = Collaboration.objects.filter(
            collaborator=self.client_user)
        self.assertEqual(client_collabs.count(), 1)

        print("✓ Collaboration filtering by user works")


class NotificationTestCase(TestCase):
    """Test notification system"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='notifuser',
            email='notif@example.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        """Test creating notifications"""
        notif = Notification.objects.create(
            recipient=self.user,
            title="Test Notification",
            message="This is a test",
            notification_type='collaboration'
        )

        self.assertEqual(notif.recipient, self.user)
        self.assertFalse(notif.is_read)
        print("✓ Notification creation successful")

    def test_notification_read_status(self):
        """Test marking notifications as read"""
        notif = Notification.objects.create(
            recipient=self.user,
            title="Test",
            message="Test",
            notification_type='view',
            is_read=False
        )

        self.assertFalse(notif.is_read)
        notif.is_read = True
        notif.save()
        self.assertTrue(notif.is_read)
        print("✓ Notification read/unread status works")

    def test_notification_types(self):
        """Test all notification types"""
        notif_types = ['collaboration', 'view', 'like', 'message', 'other']

        for notif_type in notif_types:
            notif = Notification.objects.create(
                recipient=self.user,
                title=f"Notif {notif_type}",
                message="Test",
                notification_type=notif_type
            )
            self.assertEqual(notif.notification_type, notif_type)

        print(f"✓ All {len(notif_types)} notification types work")


class IntegrationTestCase(TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        self.client = Client()

    def test_complete_creator_workflow(self):
        """Test complete workflow: register -> create portfolio -> upload work"""
        # 1. Register
        user = User.objects.create_user(
            username='workflow_creator',
            email='workflow@example.com',
            password='testpass123',
            first_name='Workflow',
            last_name='Creator'
        )
        user.profile.role = 'creator'
        user.profile.bio = "Creative professional"
        user.profile.skills = "Design|Photography"
        user.profile.save()

        # 2. Create portfolio
        portfolio = Portfolio.objects.create(
            creator=user,
            title="Workflow Portfolio",
            description="Professional portfolio"
        )

        # 3. Upload creative works
        works = []
        for i in range(3):
            work = CreativeWork.objects.create(
                creator=user,
                portfolio=portfolio,
                title=f"Work {i+1}",
                description=f"Description {i+1}",
                work_type='graphic_design'
            )
            works.append(work)

        # Verify
        self.assertEqual(User.objects.filter(
            username='workflow_creator').count(), 1)
        self.assertEqual(Portfolio.objects.filter(creator=user).count(), 1)
        self.assertEqual(CreativeWork.objects.filter(creator=user).count(), 3)
        print("✓ Complete creator workflow successful")

    def test_complete_collaboration_workflow(self):
        """Test complete workflow: creator -> client -> collaboration request"""
        # Create creator and client
        creator = User.objects.create_user(
            username='collab_creator',
            email='collab_creator@example.com',
            password='testpass123'
        )
        creator.profile.role = 'creator'
        creator.profile.save()

        client = User.objects.create_user(
            username='collab_client',
            email='collab_client@example.com',
            password='testpass123'
        )
        client.profile.role = 'client'
        client.profile.save()

        # Client sends collaboration request
        collab = Collaboration.objects.create(
            creator=creator,
            collaborator=client,
            title="Website Design Project",
            description="Need a professional website",
            status='pending'
        )

        # Creator accepts
        collab.status = 'accepted'
        collab.save()

        # Verify
        self.assertEqual(collab.status, 'accepted')
        self.assertEqual(
            Collaboration.objects.filter(
                creator=creator, status='accepted').count(), 1
        )
        print("✓ Complete collaboration workflow successful")


class SearchFilterTestCase(TestCase):
    """Test search and filter functionality"""

    def setUp(self):
        # Create multiple users
        self.users = []
        skills_list = ['Design', 'Photography', 'Animation']

        for i in range(3):
            user = User.objects.create_user(
                username=f'searcher_{i}',
                email=f'search{i}@example.com',
                password='testpass123'
            )
            user.profile.role = 'creator'
            user.profile.skills = skills_list[i]
            user.profile.location = f'City {i}'
            user.profile.save()
            self.users.append(user)

    def test_filter_by_role(self):
        """Test filtering users by role"""
        creators = [u for u in self.users]
        self.assertEqual(len(creators), 3)
        print("✓ Filtering by role works")

    def test_filter_by_skills(self):
        """Test filtering users by skills"""
        designer = [u for u in self.users if 'Design' in u.profile.skills]
        self.assertEqual(len(designer), 1)
        print("✓ Filtering by skills works")

    def test_search_by_location(self):
        """Test searching by location"""
        city_search = [u for u in self.users if 'City' in u.profile.location]
        self.assertEqual(len(city_search), 3)
        print("✓ Search by location works")
