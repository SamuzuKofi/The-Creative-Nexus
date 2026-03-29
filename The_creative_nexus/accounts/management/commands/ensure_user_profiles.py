from django.core.management.base import BaseCommand
from accounts.models import CustomUser, UserProfile


class Command(BaseCommand):
    help = 'Ensure all users have a corresponding UserProfile'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created profile for user: {user.username}')
                )
        
        # Print summary
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total profiles created/verified: {users.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ New profiles created: {created_count}')
        )
