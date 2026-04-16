"""
Test script for Registration Tracking API endpoints.
Run with: python manage.py shell < test_registration_tracking.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import StudentProfile
from apps.academics.models import Department, Course, Subject, Program
from apps.students.models import SemesterRegistration, FeeTransaction, RegisteredCourse
from datetime import date
from decimal import Decimal

User = get_user_model()

print("=" * 70)
print("Testing Registration Tracking API Setup")
print("=" * 70)

# Clean up any existing test data
User.objects.filter(username__startswith='track_test_').delete()
Department.objects.filter(code='TRACK').delete()

# Create department
dept = Department.objects.create(name='Tracking Test Dept', code='TRACK')
print(f"✓ Created department: {dept}")

# Create program
program = Program.objects.create(
    name='Test Tracking Program',
    code='TRACKPROG',
    department=dept,
    duration_years=4,
    duration_semesters=8
)
print(f"✓ Created program: {program}")

# Create course
course = Course.objects.create(
    name='Test Tracking Course',
    code='TRACK-001',
    department=dept,
    credits=160,
    duration_years=4
)
print(f"✓ Created course: {course}")

# Create subjects
subject1 = Subject.objects.create(
    name='Tracking Subject 1',
    code='TRK101',
    course=course,
    semester=1,
    credits=4
)
subject2 = Subject.objects.create(
    name='Tracking Subject 2',
    code='TRK102',
    course=course,
    semester=1,
    credits=4
)
print(f"✓ Created subjects: {subject1}, {subject2}")

# Create 3 test students
students = []
for i in range(1, 4):
    user = User.objects.create_user(
        username=f'track_test_student{i}',
        email=f'track{i}@test.com',
        password='testpass123',
        role='STUDENT',
        first_name=f'Track{i}',
        last_name='Student'
    )
    
    student_profile = StudentProfile.objects.get(user=user)
    student_profile.enrollment_number = f'TRACK2025{i:03d}'
    student_profile.department = dept
    student_profile.program = program
    student_profile.batch_year = 2025
    student_profile.current_semester = 1
    student_profile.save()
    
    students.append(student_profile)
    print(f"✓ Created student: {student_profile.enrollment_number}")

# Register only 2 out of 3 students
print("\n" + "=" * 70)
print("Creating Semester Registrations (2 out of 3 students)")
print("=" * 70)

for i, student in enumerate(students[:2], 1):  # Only first 2 students
    # Create semester registration
    semester_reg = SemesterRegistration.objects.create(
        student=student,
        academic_year='2025-26',
        semester='Jan-Jun 2026',
        institute_fee_paid=True,
        hostel_fee_paid=i == 1,  # Only first student has hostel
        hostel_room_no=f'BH-{100+i}' if i == 1 else None,
        total_credits=8
    )
    print(f"✓ Created registration for {student.enrollment_number}")
    
    # Create fee transaction
    fee_txn = FeeTransaction.objects.create(
        semester_registration=semester_reg,
        utr_no=f'UTR{2025000+i}',
        bank_name=f'Test Bank {i}',
        transaction_date=date(2025, 12, i),
        amount=Decimal('50000.00') + Decimal(i * 1000),
        account_debited=f'Student Account {i}',
        account_credited='Institute Account'
    )
    print(f"  - Fee transaction: {fee_txn.utr_no} - ₹{fee_txn.amount}")
    
    # Register courses
    reg_course1 = RegisteredCourse.objects.create(
        semester_registration=semester_reg,
        subject=subject1,
        is_backlog=False
    )
    reg_course2 = RegisteredCourse.objects.create(
        semester_registration=semester_reg,
        subject=subject2,
        is_backlog=i == 2  # Second student has one backlog
    )
    print(f"  - Registered courses: {subject1.code}, {subject2.code}")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"Total Students: {len(students)}")
print(f"Registered Students: 2")
print(f"Pending Students: 1")
print(f"Registration Rate: 66.67%")

print("\n" + "=" * 70)
print("API Endpoints Ready for Testing")
print("=" * 70)
print("\n1. Registration Tracking (Admin only):")
print("   GET /api/students/registration-tracking/?academic_year=2025-26&semester=Jan-Jun 2026")
print("   Expected: List of 3 students, 2 with has_registered=true, 1 with has_registered=false")

print("\n2. Registration Detail (Admin/Faculty):")
for i, student in enumerate(students[:2], 1):
    reg = SemesterRegistration.objects.get(student=student)
    print(f"   GET /api/students/registration-detail/{student.id}/{reg.id}/")
    print(f"   Expected: Full details for {student.enrollment_number} including UTR: UTR{2025000+i}")

print("\n" + "=" * 70)
print("✓ Test data created successfully!")
print("=" * 70)
print("\nYou can now test the endpoints using:")
print("- Swagger UI: http://127.0.0.1:8000/swagger/")
print("- Admin credentials: admin_demo / Admin@2026")
print("=" * 70)
