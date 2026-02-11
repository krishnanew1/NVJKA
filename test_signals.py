"""
Test script to verify automatic profile creation via signals.
"""
from users.models import CustomUser, StudentProfile, FacultyProfile

# Test 1: Create a student user
print("=" * 50)
print("Test 1: Creating STUDENT user")
print("=" * 50)
student_user = CustomUser.objects.create_user(
    username='test_student_signal',
    password='test123',
    role='STUDENT',
    email='student@test.com'
)
print(f"✓ User created: {student_user.username}")
print(f"✓ Role: {student_user.role}")
print(f"✓ Has student_profile: {hasattr(student_user, 'student_profile')}")
if hasattr(student_user, 'student_profile'):
    print(f"✓ Enrollment number: {student_user.student_profile.enrollment_number}")
    print(f"✓ Batch year: {student_user.student_profile.batch_year}")

# Test 2: Create a faculty user
print("\n" + "=" * 50)
print("Test 2: Creating FACULTY user")
print("=" * 50)
faculty_user = CustomUser.objects.create_user(
    username='test_faculty_signal',
    password='test123',
    role='FACULTY',
    email='faculty@test.com'
)
print(f"✓ User created: {faculty_user.username}")
print(f"✓ Role: {faculty_user.role}")
print(f"✓ Has faculty_profile: {hasattr(faculty_user, 'faculty_profile')}")
if hasattr(faculty_user, 'faculty_profile'):
    print(f"✓ Employee ID: {faculty_user.faculty_profile.employee_id}")
    print(f"✓ Department: {faculty_user.faculty_profile.department}")

# Test 3: Create an admin user (should not create profile)
print("\n" + "=" * 50)
print("Test 3: Creating ADMIN user")
print("=" * 50)
admin_user = CustomUser.objects.create_user(
    username='test_admin_signal',
    password='test123',
    role='ADMIN',
    email='admin@test.com'
)
print(f"✓ User created: {admin_user.username}")
print(f"✓ Role: {admin_user.role}")
print(f"✓ Has student_profile: {hasattr(admin_user, 'student_profile')}")
print(f"✓ Has faculty_profile: {hasattr(admin_user, 'faculty_profile')}")

print("\n" + "=" * 50)
print("All tests completed!")
print("=" * 50)

# Cleanup
print("\nCleaning up test users...")
student_user.delete()
faculty_user.delete()
admin_user.delete()
print("✓ Test users deleted")
