"""
Django management command to create an admin user.

Usage:
    python manage.py create_admin
    python manage.py create_admin --username admin --email admin@example.com
    python manage.py create_admin --username admin --password MySecurePass123
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an admin user with superuser privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin user'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user (will prompt if not provided)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name for the admin user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name for the admin user'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number for the admin user'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Admin User Creation'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        try:
            with transaction.atomic():
                # Get username
                username = options.get('username')
                if not username:
                    username = input('Username: ').strip()
                    if not username:
                        self.stdout.write(self.style.ERROR('Username cannot be empty'))
                        return
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.ERROR(f'\n✗ User with username "{username}" already exists'))
                    return
                
                # Get email
                email = options.get('email')
                if not email:
                    email = input('Email: ').strip()
                    if not email:
                        self.stdout.write(self.style.ERROR('Email cannot be empty'))
                        return
                
                # Check if email already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.ERROR(f'\n✗ User with email "{email}" already exists'))
                    return
                
                # Get password
                password = options.get('password')
                if not password:
                    while True:
                        password = getpass.getpass('Password: ')
                        if not password:
                            self.stdout.write(self.style.ERROR('Password cannot be empty'))
                            continue
                        
                        password_confirm = getpass.getpass('Password (again): ')
                        if password != password_confirm:
                            self.stdout.write(self.style.ERROR('Passwords do not match. Try again.'))
                            continue
                        
                        break
                
                # Get optional fields
                first_name = options.get('first_name')
                if not first_name:
                    first_name = input('First name (optional): ').strip() or 'Admin'
                
                last_name = options.get('last_name')
                if not last_name:
                    last_name = input('Last name (optional): ').strip() or 'User'
                
                phone = options.get('phone')
                if not phone:
                    phone = input('Phone number (optional): ').strip() or ''
                
                # Create admin user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone,
                    role='ADMIN',
                    is_staff=True,
                    is_superuser=True
                )
                
                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('✓ Admin user created successfully!'))
                self.stdout.write(self.style.SUCCESS('='*60))
                self.stdout.write('\nUser Details:')
                self.stdout.write(f'  Username:   {user.username}')
                self.stdout.write(f'  Email:      {user.email}')
                self.stdout.write(f'  Name:       {user.get_full_name()}')
                self.stdout.write(f'  Role:       {user.role}')
                self.stdout.write(f'  Staff:      {user.is_staff}')
                self.stdout.write(f'  Superuser:  {user.is_superuser}')
                if phone:
                    self.stdout.write(f'  Phone:      {phone}')
                self.stdout.write('\nYou can now log in with these credentials!')
                self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\nOperation cancelled by user'))
            return
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error creating admin user: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise
