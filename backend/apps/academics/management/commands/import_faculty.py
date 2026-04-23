"""
Management command to import faculty data from CSV file.

CSV Format:
name,email,phone,designation,department_code,specialization,employee_id

Example:
Dr. John Smith,john.smith@example.com,1234567890,Professor,CS,Machine Learning,FAC2024001
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.academics.models import Department
from apps.users.models import FacultyProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Import faculty data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file containing faculty data'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Faculty@2026',
            help='Default password for all faculty accounts (default: Faculty@2026)'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip faculty members that already exist (by email or employee_id)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually creating records'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        default_password = options['password']
        skip_existing = options['skip_existing']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV headers
                required_fields = ['name', 'email', 'designation', 'department_code', 'employee_id']
                if not all(field in reader.fieldnames for field in required_fields):
                    raise CommandError(
                        f'CSV must contain these columns: {", ".join(required_fields)}\n'
                        f'Found columns: {", ".join(reader.fieldnames)}'
                    )

                faculty_data = list(reader)
                total_count = len(faculty_data)
                created_count = 0
                skipped_count = 0
                error_count = 0

                self.stdout.write(f'Found {total_count} faculty records in CSV')
                self.stdout.write('Starting import...\n')

                for idx, row in enumerate(faculty_data, 1):
                    try:
                        result = self._import_faculty(
                            row,
                            default_password,
                            skip_existing,
                            dry_run
                        )
                        
                        if result == 'created':
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'[{idx}/{total_count}] ✓ Created: {row["name"]} ({row["employee_id"]})'
                                )
                            )
                        elif result == 'skipped':
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'[{idx}/{total_count}] ⊘ Skipped: {row["name"]} ({row["employee_id"]}) - Already exists'
                                )
                            )
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'[{idx}/{total_count}] ✗ Error: {row["name"]} ({row["employee_id"]}) - {str(e)}'
                            )
                        )

                # Summary
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS(f'Import Summary:'))
                self.stdout.write(f'  Total records: {total_count}')
                self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
                if skipped_count > 0:
                    self.stdout.write(self.style.WARNING(f'  Skipped: {skipped_count}'))
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f'  Errors: {error_count}'))
                self.stdout.write('='*60)

                if dry_run:
                    self.stdout.write(self.style.WARNING('\nDRY RUN COMPLETE - No changes were made'))

        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

    @transaction.atomic
    def _import_faculty(self, row, default_password, skip_existing, dry_run):
        """Import a single faculty member."""
        
        # Extract data from row
        name = row['name'].strip()
        email = row['email'].strip().lower()
        phone = row.get('phone', '').strip()
        designation = row['designation'].strip()
        department_code = row['department_code'].strip().upper()
        specialization = row.get('specialization', '').strip()
        employee_id = row['employee_id'].strip()

        # Check if faculty already exists
        if User.objects.filter(email=email).exists():
            if skip_existing:
                return 'skipped'
            else:
                raise ValueError(f'User with email {email} already exists')

        if FacultyProfile.objects.filter(employee_id=employee_id).exists():
            if skip_existing:
                return 'skipped'
            else:
                raise ValueError(f'Faculty with employee_id {employee_id} already exists')

        # Get department
        try:
            department = Department.objects.get(code=department_code)
        except Department.DoesNotExist:
            raise ValueError(f'Department with code {department_code} not found')

        if dry_run:
            return 'created'

        # Generate username from name (lowercase, replace spaces with underscores)
        username = name.lower().replace(' ', '_').replace('.', '')
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        # Split name into first and last name
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=default_password,
            first_name=first_name,
            last_name=last_name,
            role='FACULTY',
            phone_number=phone if phone else None,
            is_active=True
        )

        # Create faculty profile
        FacultyProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department=department,
            designation=designation,
            specialization=specialization if specialization else None
        )

        return 'created'
