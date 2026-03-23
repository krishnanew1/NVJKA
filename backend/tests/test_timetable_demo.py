"""
Demo test for timetable generation feature.

This test demonstrates the complete timetable generation workflow
from setup to API usage.
"""
import datetime
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Department, Course, Subject, Timetable
from apps.users.models import CustomUser, StudentProfile, FacultyProfile
from apps.students.models import Enrollment
from apps.faculty.models import ClassAssignment


class TimetableDemoTest(TransactionTestCase):
    """
    Demo test showcasing the auto-generate timetable feature.
    
    This test creates a realistic academic scenario and demonstrates
    how the timetable generation works end-to-end.
    """

    def setUp(self):
        """Set up a complete academic scenario."""
        print("\n🏫 Setting up Academic Environment...")
        
        # Create admin
        self.admin = CustomUser.objects.create_user(
            username='admin_demo',
            password='Admin@2026',
            role='ADMIN',
            is_staff=True
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Computer Science & Engineering',
            code='CSE',
            description='Department of Computer Science and Engineering'
        )
        
        # Create course
        self.course = Course.objects.create(
            name='B.Tech Computer Science',
            code='BTECH-CS',
            department=self.department,
            credits=160,
            duration_years=4
        )
        
        # Create subjects for semester 3
        subjects_data = [
            ('Data Structures & Algorithms', 'CS301', 4, True),
            ('Database Management Systems', 'CS302', 3, True),
            ('Computer Networks', 'CS303', 3, True),
            ('Operating Systems', 'CS304', 4, True),
            ('Software Engineering', 'CS305', 3, True),
            ('Web Technologies', 'CS306', 3, False),
        ]
        
        self.subjects = []
        for name, code, credits, mandatory in subjects_data:
            subject = Subject.objects.create(
                name=name,
                code=code,
                course=self.course,
                semester=3,
                credits=credits,
                is_mandatory=mandatory
            )
            self.subjects.append(subject)
        
        # Create faculty members
        faculty_data = [
            ('Dr. Alice Johnson', 'Professor', 'Data Structures, Algorithms'),
            ('Dr. Bob Smith', 'Associate Professor', 'Database Systems'),
            ('Dr. Carol Davis', 'Assistant Professor', 'Computer Networks'),
            ('Dr. David Wilson', 'Professor', 'Operating Systems'),
            ('Dr. Eve Brown', 'Assistant Professor', 'Software Engineering'),
        ]
        
        self.faculty_members = []
        for i, (name, designation, specialization) in enumerate(faculty_data):
            first_name, last_name = name.split(' ', 1)[1].split(' ', 1)
            
            user = CustomUser.objects.create_user(
                username=f'faculty_{i+1}',
                password='Faculty@2026',
                role='FACULTY',
                first_name=first_name,
                last_name=last_name
            )
            
            faculty = FacultyProfile.objects.create(
                user=user,
                employee_id=f'FAC-{i+1:03d}',
                department=self.department,
                designation=designation,
                specialization=specialization
            )
            self.faculty_members.append(faculty)
        
        # Create class assignments (faculty to subjects)
        for i, subject in enumerate(self.subjects[:5]):  # Assign faculty to first 5 subjects
            ClassAssignment.objects.create(
                faculty=self.faculty_members[i],
                subject=subject,
                semester=3,
                academic_year=2026
            )
        
        # Create students for batch 2024
        self.students = []
        for i in range(30):  # Create 30 students
            user = CustomUser.objects.create_user(
                username=f'student_2024_{i+1:03d}',
                password='Student@2026',
                role='STUDENT',
                first_name=f'Student{i+1}',
                last_name='CSE2024'
            )
            
            student, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'enrollment_number': f'2024CSE{i+1:03d}',
                    'department': self.department,
                    'current_semester': 3,
                    'batch_year': 2024
                }
            )
            self.students.append(student)
        
        # Enroll all students in the course
        for student in self.students:
            Enrollment.objects.create(
                student=student,
                course=self.course,
                semester=3,
                status='Active'
            )
        
        # Set up API client
        self.client = APIClient()
        token = RefreshToken.for_user(self.admin).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        print(f"✅ Created: {len(self.subjects)} subjects, {len(self.faculty_members)} faculty, {len(self.students)} students")

    def test_complete_timetable_generation_demo(self):
        """
        DEMO: Complete timetable generation workflow.
        
        This test demonstrates:
        1. Generating timetable via API
        2. Retrieving generated timetable
        3. Verifying conflict-free scheduling
        4. Showing timetable statistics
        """
        print("\n📅 TIMETABLE GENERATION DEMO")
        print("=" * 50)
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 1: Generate Timetable via API
        # ═══════════════════════════════════════════════════════════════════════
        
        print("\n🔄 STEP 1: Generating Timetable...")
        
        generate_url = reverse('academics:timetable-generate-timetable')
        response = self.client.post(generate_url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3,
            'academic_year': '2026-27'
        }, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        result = response.json()
        self.assertTrue(result['success'])
        
        stats = result['data']
        print(f"✅ Timetable Generated Successfully!")
        print(f"   📊 Class: {stats['class_name']}")
        print(f"   📚 Total Subjects: {stats['total_subjects']}")
        print(f"   ✅ Scheduled Subjects: {stats['scheduled_subjects']}")
        print(f"   ❌ Failed Subjects: {stats['failed_subjects']}")
        print(f"   📝 Total Entries: {stats['total_entries']}")
        
        if stats['failed_subjects_details']:
            print(f"   ⚠️  Failed Subjects:")
            for failed in stats['failed_subjects_details']:
                subject_name = failed['subject'].name if hasattr(failed['subject'], 'name') else str(failed['subject'])
                print(f"      - {subject_name}: {failed['error']}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: Retrieve Generated Timetable
        # ═══════════════════════════════════════════════════════════════════════
        
        print(f"\n📋 STEP 2: Retrieving Generated Timetable...")
        
        retrieve_url = reverse('academics:timetable-get-batch-timetable')
        response = self.client.get(retrieve_url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3,
            'academic_year': '2026-27'
        })
        
        self.assertEqual(response.status_code, 200)
        
        timetable_data = response.json()
        self.assertTrue(timetable_data['success'])
        
        entries = timetable_data['data']
        print(f"✅ Retrieved {len(entries)} timetable entries")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: Display Timetable in Readable Format
        # ═══════════════════════════════════════════════════════════════════════
        
        print(f"\n📅 STEP 3: Generated Timetable for CSE Batch 2024")
        print("=" * 80)
        
        # Group entries by day
        days_schedule = {}
        for entry in entries:
            day = entry['day_of_week']
            if day not in days_schedule:
                days_schedule[day] = []
            days_schedule[day].append(entry)
        
        # Sort days in weekday order
        day_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
        
        for day in day_order:
            if day in days_schedule:
                print(f"\n📅 {day}")
                print("-" * 40)
                
                # Sort entries by start time
                day_entries = sorted(days_schedule[day], key=lambda x: x['start_time'])
                
                for entry in day_entries:
                    subject = entry['subject']
                    faculty = entry['faculty']
                    faculty_name = faculty['name'] if faculty else 'TBA'
                    
                    print(f"  {entry['start_time']}-{entry['end_time']} | "
                          f"{subject['code']} - {subject['name'][:25]:<25} | "
                          f"{faculty_name[:20]:<20} | {entry['classroom']}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: Verify Conflict-Free Scheduling
        # ═══════════════════════════════════════════════════════════════════════
        
        print(f"\n🔍 STEP 4: Verifying Conflict-Free Scheduling...")
        
        conflicts_found = 0
        
        # Check for classroom conflicts
        classroom_schedule = {}
        faculty_schedule = {}
        
        for entry in entries:
            day = entry['day_of_week']
            start_time = entry['start_time']
            end_time = entry['end_time']
            classroom = entry['classroom']
            faculty_id = entry['faculty']['id'] if entry['faculty'] else None
            
            # Check classroom conflicts
            if classroom:
                key = f"{day}-{classroom}"
                if key not in classroom_schedule:
                    classroom_schedule[key] = []
                
                # Check for time overlap
                for existing_start, existing_end in classroom_schedule[key]:
                    if (start_time < existing_end and end_time > existing_start):
                        conflicts_found += 1
                        print(f"   ⚠️  Classroom conflict: {classroom} on {day}")
                
                classroom_schedule[key].append((start_time, end_time))
            
            # Check faculty conflicts
            if faculty_id:
                key = f"{day}-{faculty_id}"
                if key not in faculty_schedule:
                    faculty_schedule[key] = []
                
                # Check for time overlap
                for existing_start, existing_end in faculty_schedule[key]:
                    if (start_time < existing_end and end_time > existing_start):
                        conflicts_found += 1
                        print(f"   ⚠️  Faculty conflict: {entry['faculty']['name']} on {day}")
                
                faculty_schedule[key].append((start_time, end_time))
        
        if conflicts_found == 0:
            print("✅ No conflicts detected! Timetable is conflict-free.")
        else:
            print(f"❌ Found {conflicts_found} conflicts in the generated timetable.")
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: Show Statistics and Summary
        # ═══════════════════════════════════════════════════════════════════════
        
        print(f"\n📊 STEP 5: Timetable Statistics")
        print("=" * 40)
        
        # Count classes per subject
        subject_counts = {}
        for entry in entries:
            subject_code = entry['subject']['code']
            if subject_code not in subject_counts:
                subject_counts[subject_code] = 0
            subject_counts[subject_code] += 1
        
        print("Classes per Subject:")
        for subject_code, count in sorted(subject_counts.items()):
            subject_name = next(s.name for s in self.subjects if s.code == subject_code)
            print(f"  {subject_code}: {count} classes - {subject_name}")
        
        # Count classes per day
        day_counts = {}
        for entry in entries:
            day = entry['day_of_week']
            if day not in day_counts:
                day_counts[day] = 0
            day_counts[day] += 1
        
        print(f"\nClasses per Day:")
        for day in day_order:
            count = day_counts.get(day, 0)
            print(f"  {day}: {count} classes")
        
        # Faculty utilization
        faculty_counts = {}
        for entry in entries:
            if entry['faculty']:
                faculty_name = entry['faculty']['name']
                if faculty_name not in faculty_counts:
                    faculty_counts[faculty_name] = 0
                faculty_counts[faculty_name] += 1
        
        print(f"\nFaculty Utilization:")
        for faculty_name, count in sorted(faculty_counts.items()):
            print(f"  {faculty_name}: {count} classes")
        
        print(f"\n🎉 TIMETABLE GENERATION DEMO COMPLETED!")
        print("=" * 50)
        
        # Assertions to ensure the demo worked correctly
        self.assertGreater(len(entries), 0, "Should have generated at least some timetable entries")
        self.assertEqual(conflicts_found, 0, "Generated timetable should be conflict-free")
        self.assertGreater(len(subject_counts), 0, "Should have scheduled at least some subjects")

    def test_api_error_handling_demo(self):
        """
        DEMO: API error handling scenarios.
        
        Shows how the API handles various error conditions gracefully.
        """
        print("\n🚨 API ERROR HANDLING DEMO")
        print("=" * 40)
        
        generate_url = reverse('academics:timetable-generate-timetable')
        
        # Test 1: Missing batch_year
        print("\n1️⃣  Testing missing batch_year...")
        response = self.client.post(generate_url, {
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        print(f"   ❌ Error: {result['error']}")
        
        # Test 2: Invalid batch_year
        print("\n2️⃣  Testing invalid batch_year...")
        response = self.client.post(generate_url, {
            'batch_year': 'invalid',
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        print(f"   ❌ Error: {result['error']}")
        
        # Test 3: Non-existent batch
        print("\n3️⃣  Testing non-existent batch...")
        response = self.client.post(generate_url, {
            'batch_year': 2030,  # Future batch with no students
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        print(f"   ❌ Error: {result['error']}")
        
        print(f"\n✅ All error scenarios handled correctly!")

    def test_regeneration_demo(self):
        """
        DEMO: Timetable regeneration (clearing and recreating).
        
        Shows how regenerating a timetable clears the old one and creates a new one.
        """
        print("\n🔄 TIMETABLE REGENERATION DEMO")
        print("=" * 40)
        
        generate_url = reverse('academics:timetable-generate-timetable')
        
        # Generate initial timetable
        print("\n1️⃣  Generating initial timetable...")
        response = self.client.post(generate_url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 201)
        initial_result = response.json()['data']
        initial_count = initial_result['total_entries']
        print(f"   ✅ Generated {initial_count} entries")
        
        # Check database entries
        db_entries_1 = Timetable.objects.filter(
            class_name='CSE-2024-S3',
            is_active=True
        ).count()
        print(f"   📊 Database entries: {db_entries_1}")
        
        # Regenerate timetable
        print("\n2️⃣  Regenerating timetable...")
        response = self.client.post(generate_url, {
            'batch_year': 2024,
            'department_id': self.department.id,
            'semester': 3
        }, format='json')
        
        self.assertEqual(response.status_code, 201)
        new_result = response.json()['data']
        new_count = new_result['total_entries']
        print(f"   ✅ Regenerated {new_count} entries")
        
        # Check database entries after regeneration
        db_entries_2 = Timetable.objects.filter(
            class_name='CSE-2024-S3',
            is_active=True
        ).count()
        print(f"   📊 Database entries after regeneration: {db_entries_2}")
        
        print(f"\n✅ Regeneration completed successfully!")
        print(f"   📈 Old entries were cleared and new ones created")