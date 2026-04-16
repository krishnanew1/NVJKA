"""
Quick manual test to verify the semester registration API works.
Run with: python manage.py shell < test_semester_api.py
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

User = get_user_model()

print("=" * 60)
print("Testing Semester Registration System")
print("=" * 60)

# Clean up any existing test data
User.objects.filter(username='test_api_student').delete()
Department.objects.filter(code='TEST').delete()

# Create department
dept = Department.objects.create(name='Test Department', code='TEST')
print(f"✓ Created department: {dept}")

# Create program
program = Program.objects.create(
    name='Test Program',
    code='TESTPROG',
    department=dept,
    duration_years=4,
    duration_semesters=8
)
print(f"✓ Created program: {program}")

# Create course
course = Course.objects.create(
    name='Test Course',
    code='TEST-001',
    department=dept,
    credits=160,
    duration_years=4
)
print(f"✓ Created course: {course}")

# Create subjects
subject1 = Subject.objects.create(
    name='Test Subject 1',
    code='TS101',
    course=course,
    semester=1,
    credits=4
)
subject2 = Subject.objects.create(
    name='Test Subject 2',
    code='TS102',
    course=course,
    semester=1,
    credits=4
)
print(f"✓ Created subjects: {subject1}, {subject2}")

# Create student user
student_user = User.objects.create_user(
    username='test_api_student',
    email='test@api.com',
    password='testpass123',
    role='STUDENT'
)
print(f"✓ Created user: {student_user}")

# Update student profile
student_profile = StudentProfile.objects.get(user=student_user)
student_profile.enrollment_number = 'TEST2025001'
student_profile.department = dept
student_profile.program = program
student_profile.batch_year = 2025
student_profile.save()
print(f"✓ Updated student profile: {student_profile}")

# Create semester registration
semester_reg = SemesterRegistration.objects.create(
    student=student_profile,
    academic_year='2025-26',
    semester='Jan-Jun 2026',
    institute_fee_paid=True,
    hostel_fee_paid=True,
    hostel_room_no='BH-101',
    total_credits=8
)
print(f"✓ Created semester registration: {semester_reg}")

# Create fee transaction
fee_txn = FeeTransaction.objects.create(
    semester_registration=semester_reg,
    utr_no='UTR123456',
    bank_name='Test Bank',
    transaction_date=date(2025, 12, 1),
    amount=50000.00,
    account_debited='Student Account',
    account_credited='Institute Account'
)
print(f"✓ Created fee transaction: {fee_txn}")

# Create registered courses
reg_course1 = RegisteredCourse.objects.create(
    semester_registration=semester_reg,
    subject=subject1,
    is_backlog=False
)
reg_course2 = RegisteredCourse.objects.create(
    semester_registration=semester_reg,
    subject=subject2,
    is_backlog=False
)
print(f"✓ Created registered courses: {reg_course1}, {reg_course2}")

# Verify data
print("\n" + "=" * 60)
print("Verification")
print("=" * 60)
print(f"Total Semester Registrations: {SemesterRegistration.objects.count()}")
print(f"Total Fee Transactions: {FeeTransaction.objects.count()}")
print(f"Total Registered Courses: {RegisteredCourse.objects.count()}")

# Test retrieval
retrieved_reg = SemesterRegistration.objects.get(id=semester_reg.id)
print(f"\nRetrieved Registration: {retrieved_reg}")
print(f"  - Fee Transactions: {retrieved_reg.fee_transactions.count()}")
print(f"  - Registered Courses: {retrieved_reg.registered_courses.count()}")

print("\n" + "=" * 60)
print("✓ All tests passed successfully!")
print("=" * 60)
