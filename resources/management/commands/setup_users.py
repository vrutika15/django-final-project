from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update admin and superadmin users with the same password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123',
            help='Password for both admin and superadmin users (default: Admin@123)'
        )

    def handle(self, *args, **options):
        password = options['password']
        
        users_to_manage = [
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
        updated_count = 0

        for user_data in users_to_manage:
            username = user_data['username']
            
            user, created = User.objects.get_or_create(username=username, defaults={
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
            })

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user "{username}" "')
                )
                created_count += 1
            else:
                user.set_password(password)
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated existing user "{username}" "')
                )
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSummary: {created_count} created, {updated_count} updated')
        )
        # self.stdout.write(
        #     self.style.SUCCESS(
        #         '\nLogin credentials:\n'
        #         f'Username: admin | Password: {password}\n'
        #         f'Username: superadmin | Password: {password}'
        #     )
        # )
