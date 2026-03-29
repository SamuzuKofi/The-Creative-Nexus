from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Portfolio, CreativeWork, Collaboration, Project, Notification, Rating
from accounts.models import UserProfile
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing data...")
            CreativeWork.objects.all().delete()
            Portfolio.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(username__startswith='test_').delete()
            self.stdout.write(self.style.SUCCESS("✓ Data cleared"))

        # Sample data
        roles = ['creator', 'client', 'mentor', 'admin']

        sample_creators = [
            {
                'username': 'test_designer_ama',
                'email': 'ama@example.com',
                'first_name': 'Ama',
                'last_name': 'Osei',
                'role': 'creator',
                'bio': 'Passionate graphic designer from Accra with 5 years of experience in brand design.',
                'location': 'Accra, Ghana',
                'skills': 'Graphic Design|UI/UX|Adobe Creative Suite|Branding',
                'website': 'https://example.com/ama',
                'years_experience': 5,
            },
            {
                'username': 'test_animator_kwesi',
                'email': 'kwesi@example.com',
                'first_name': 'Kwesi',
                'last_name': 'Mensah',
                'role': 'creator',
                'bio': '3D animator and motion graphics artist. Specializes in character animation.',
                'location': 'Kumasi, Ghana',
                'skills': '3D Animation|Motion Graphics|Blender|Cinema 4D',
                'website': 'https://example.com/kwesi',
                'years_experience': 3,
            },
            {
                'username': 'test_photographer_akosua',
                'email': 'akosua@example.com',
                'first_name': 'Akosua',
                'last_name': 'Appiah',
                'role': 'creator',
                'bio': 'Documentary and fashion photographer capturing stories across West Africa.',
                'location': 'Takoradi, Ghana',
                'skills': 'Photography|Photoshop|Lightroom|Fashion|Documentary',
                'website': 'https://example.com/akosua',
                'years_experience': 6,
            },
            {
                'username': 'test_developer_kofi',
                'email': 'kofi@example.com',
                'first_name': 'Kofi',
                'last_name': 'Boateng',
                'role': 'creator',
                'bio': 'Full-stack developer passionate about building fintech solutions for Africa.',
                'location': 'Accra, Ghana',
                'skills': 'Python|JavaScript|Web Design|Mobile App Dev|Django',
                'website': 'https://example.com/kofi',
                'years_experience': 4,
            },
            {
                'username': 'test_writer_zainab',
                'email': 'zainab@example.com',
                'first_name': 'Zainab',
                'last_name': 'Hassan',
                'role': 'creator',
                'bio': 'Content writer and brand strategist helping creative businesses grow.',
                'location': 'Accra, Ghana',
                'skills': 'Content Writing|Copywriting|SEO|Brand Strategy|Social Media',
                'website': 'https://example.com/zainab',
                'years_experience': 4,
            },
        ]

        sample_clients = [
            {
                'username': 'test_client_asante',
                'email': 'client1@example.com',
                'first_name': 'Asante',
                'last_name': 'Adom',
                'role': 'client',
                'bio': 'Small business owner looking to build a strong brand.',
                'location': 'Accra, Ghana',
                'skills': 'Business Management|Marketing',
                'years_experience': 0,
            },
            {
                'username': 'test_client_ek',
                'email': 'client2@example.com',
                'first_name': 'Ekow',
                'last_name': 'Kuma',
                'role': 'client',
                'bio': 'Startup founder looking for creative talent.',
                'location': 'Tema, Ghana',
                'skills': 'Startup Development|Tech',
                'years_experience': 2,
            },
        ]

        sample_mentors = [
            {
                'username': 'test_mentor_yaw',
                'email': 'mentor@example.com',
                'first_name': 'Yaw',
                'last_name': 'Asare',
                'role': 'mentor',
                'bio': 'Creative industry mentor with 15+ years of experience. Available for guidance.',
                'location': 'Accra, Ghana',
                'skills': 'Mentoring|Creative Strategy|Business Development|Industry Expertise',
                'website': 'https://example.com/yaw',
                'years_experience': 15,
            },
        ]

        # Create all users
        all_users = sample_creators + sample_clients + sample_mentors
        created_users = {}

        # Store usernames for later
        creator_usernames = [u['username'] for u in sample_creators]
        client_usernames = [u['username'] for u in sample_clients]
        mentor_usernames = [u['username'] for u in sample_mentors]

        for user_data in all_users:
            username = user_data.pop('username')
            email = user_data.pop('email')
            role = user_data.pop('role')

            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    f"⊘ User {username} already exists, skipping")
                created_users[username] = User.objects.get(username=username)
                continue

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=user_data.pop('first_name'),
                last_name=user_data.pop('last_name'),
                email_verified=True,
                is_active=True,
            )
            created_users[username] = user

            # Update auto-created profile (Django signals create it automatically)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            for key, value in user_data.items():
                setattr(profile, key, value)
            profile.save()

            self.stdout.write(self.style.SUCCESS(
                f"✓ Created user: {username} ({role})"))

        # Create portfolios and creative works for creators
        work_titles = [
            'Brand Identity Design',
            'Website Redesign',
            'Character Animation Series',
            'Fashion Photography Collection',
            'Product Photography',
            'Mobile App Interface',
            'Marketing Campaign Design',
            'Documentary Portfolio',
            'Digital Art Series',
            'Animation Reel',
        ]

        work_descriptions = [
            'A complete rebranding project for a local startup.',
            'Modern and responsive website design for e-commerce.',
            'Character animation series for educational content.',
            'High fashion photography featuring local talents.',
            'Professional product photography for online store.',
            'User-friendly mobile app interface design.',
            'Complete marketing campaign including visuals and copy.',
            'Documentary photos from community events.',
            'Digital art exploring African themes and culture.',
            'Professional animation reel showcasing skills.',
        ]

        for username, user in created_users.items():
            if user.profile.role == 'creator':
                # Create portfolio
                portfolio, created = Portfolio.objects.get_or_create(
                    creator=user,
                    defaults={
                        'title': f"{user.get_full_name()}'s Portfolio",
                        'description': f"Creative work portfolio by {user.get_full_name()}",
                        'total_views': random.randint(10, 500),
                        'total_likes': random.randint(5, 200),
                    }
                )

                if created:
                    self.stdout.write(f"  ✓ Created portfolio for {username}")

                # Create 2-3 creative works
                num_works = random.randint(2, 3)
                for i in range(num_works):
                    work_title = random.choice(work_titles)
                    CreativeWork.objects.get_or_create(
                        creator=user,
                        portfolio=portfolio,
                        title=f"{work_title} #{i+1}",
                        defaults={
                            'description': random.choice(work_descriptions),
                            'work_type': random.choice(['digital_art', 'graphic_design', 'animation', 'photography', 'video', 'music']),
                            'is_featured': random.choice([True, False]),
                            'views': random.randint(10, 300),
                            'likes': random.randint(5, 100),
                        }
                    )

                self.stdout.write(
                    f"  ✓ Created {num_works} creative works for {username}")

        # Create some collaborations
        creators = [u for u in created_users.values()
                    if u.profile.role == 'creator']
        clients = [u for u in created_users.values()
                   if u.profile.role == 'client']

        if creators and clients:
            for i in range(min(3, len(creators), len(clients))):
                collab_statuses = ['pending',
                                   'accepted', 'completed', 'rejected']
                Collaboration.objects.get_or_create(
                    creator=creators[i],
                    collaborator=clients[i],
                    defaults={
                        'title': f"Collaboration Project #{i+1}",
                        'description': f"Creative collaboration between {creators[i].get_full_name()} and {clients[i].get_full_name()}",
                        'status': random.choice(collab_statuses),
                        'required_skills': 'Design|Creativity|Communication',
                        'timeline': '2-4 weeks',
                        'budget_range': f"${random.randint(500, 5000)}",
                    }
                )

            self.stdout.write(self.style.SUCCESS(
                f"✓ Created sample collaborations"))

        # Create notifications
        if created_users:
            all_users_list = list(created_users.values())
            notification_messages = [
                'Someone liked your work!',
                'You have a new collaboration request',
                'Your portfolio was viewed',
                'New message from a collaborator',
                'Your work was featured!',
            ]

            for i in range(5):
                user = random.choice(all_users_list)
                Notification.objects.create(
                    recipient=user,
                    title=f"Notification #{i+1}",
                    message=random.choice(notification_messages),
                    notification_type=random.choice(
                        ['collaboration', 'view', 'like', 'message', 'other']),
                    is_read=random.choice([True, False]),
                )

            self.stdout.write(self.style.SUCCESS(
                f"✓ Created sample notifications"))

        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(self.style.SUCCESS(
            "✓ Database populated successfully!"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write("\nTest Credentials:")
        self.stdout.write("-" * 50)
        self.stdout.write("All test users have password: testpass123")
        self.stdout.write("\nCreators:")
        for username in creator_usernames:
            self.stdout.write(f"  • {username}")
        self.stdout.write("\nClients:")
        for username in client_usernames:
            self.stdout.write(f"  • {username}")
        self.stdout.write("\nMentors:")
        for username in mentor_usernames:
            self.stdout.write(f"  • {username}")
        self.stdout.write("-" * 50)
