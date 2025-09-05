from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create admin and superadmin users with the same password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123',
            help='Password for both admin and superadmin users (default: Admin@123)'
        )

    def handle(self, *args, **options):
        password = options['password']
        
        users_to_create = [
            {
                'username': 'admin',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Admin',
                'last_name': 'User'
            },
            {
                'username': 'superadmin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Super',
                'last_name': 'Admin'
            }
        ]
        
        created_count = 0
        for user_data in users_to_create:
            username = user_data['username']
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists, skipping...')
                )
                continue
            
            user = User.objects.create_user(
                username=username,
                password=password,
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created user "{username}" with password "{password}"'
                )
            )
            created_count += 1
        
        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('No new users were created. Both admin and superadmin already exist.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} user(s) successfully!')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nLogin credentials:\n'
                f'Username: admin | Password: {password}\n'
                f'Username: superadmin | Password: {password}'
            )
        )
