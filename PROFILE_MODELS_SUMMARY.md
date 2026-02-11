# Profile Models Implementation Summary

## Created Models

### 1. StudentProfile Model
Located in `users/models.py`

**Fields:**
- `user` - OneToOneField to CustomUser (CASCADE delete)
- `enrollment_number` - CharField, unique, max_length=20
- `department` - ForeignKey to academics.Department (SET_NULL)
- `current_semester` - IntegerField, default=1, validated >= 1
- `batch_year` - IntegerField (e.g., 2026)
- `created_at` - DateTimeField (auto)
- `updated_at` - DateTimeField (auto)

**Features:**
- Related name: `user.student_profile`
- Reverse relation: `department.students`
- Ordering by batch_year and enrollment_number
- String representation shows enrollment number and student name

### 2. FacultyProfile Model
Located in `users/models.py`

**Fields:**
- `user` - OneToOneField to CustomUser (CASCADE delete)
- `employee_id` - CharField, unique, max_length=20
- `department` - ForeignKey to academics.Department (CASCADE)
- `designation` - CharField, max_length=100 (e.g., Professor, Lecturer)
- `specialization` - CharField, max_length=200 (optional)
- `date_of_joining` - DateField (optional)
- `created_at` - DateTimeField (auto)
- `updated_at` - DateTimeField (auto)

**Features:**
- Related name: `user.faculty_profile`
- Reverse relation: `department.faculty_members`
- Ordering by department and designation
- String representation shows employee ID, name, and designation

## Admin Configuration

Both models are registered in Django admin with:
- Custom list displays showing key information
- Search functionality across user fields
- Filtering by department, batch/designation
- Raw ID fields for user selection (better performance)
- Collapsible timestamp sections
- Custom methods to display user full names

## Database Migration

Migration created: `users/migrations/0003_studentprofile_facultyprofile.py`
- Successfully applied to database
- Tables created: `users_studentprofile` and `users_facultyprofile`

## Access in Admin Panel

Visit: http://127.0.0.1:8000/admin/

You can now:
- Create and manage Student Profiles
- Create and manage Faculty Profiles
- Link profiles to existing CustomUser accounts
- View all profile information in organized fieldsets

## Usage Examples

### Creating a Student Profile
```python
from users.models import CustomUser, StudentProfile
from academics.models import Department

# Create or get user
user = CustomUser.objects.create_user(
    username='student001',
    role='STUDENT',
    email='student@example.com'
)

# Create student profile
dept = Department.objects.get(code='CS')
student = StudentProfile.objects.create(
    user=user,
    enrollment_number='2026CS001',
    department=dept,
    current_semester=1,
    batch_year=2026
)

# Access profile from user
print(user.student_profile.enrollment_number)
```

### Creating a Faculty Profile
```python
from users.models import CustomUser, FacultyProfile
from academics.models import Department

# Create or get user
user = CustomUser.objects.create_user(
    username='faculty001',
    role='FACULTY',
    email='faculty@example.com'
)

# Create faculty profile
dept = Department.objects.get(code='CS')
faculty = FacultyProfile.objects.create(
    user=user,
    employee_id='FAC2026001',
    department=dept,
    designation='Professor',
    specialization='Machine Learning'
)

# Access profile from user
print(user.faculty_profile.designation)
```

## Next Steps

Task 6.1 from the spec is now complete. Next tasks:
- 6.2: Create profile serializers and API endpoints
- 6.3: Write property test for role-based dashboard access
- 6.4: Write property test for role-based endpoint access
