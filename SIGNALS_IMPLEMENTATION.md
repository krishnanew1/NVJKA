# Automatic Profile Creation via Django Signals

## Implementation Summary

### 1. Created `users/signals.py`

This file contains signal handlers that automatically create user profiles when a CustomUser is created.

**Signal Handlers:**

#### `create_user_profile`
- Listens to `post_save` signal on `CustomUser` model
- Triggers only when `created=True` (new user)
- **For STUDENT role**: Automatically creates a `StudentProfile` with:
  - `enrollment_number`: Temporary value `TEMP_{user.id}` (should be updated)
  - `batch_year`: Default 2026 (should be updated)
  - `department`: None (optional, can be set later)
  
- **For FACULTY role**: Profile creation is skipped because:
  - `department` field is required (non-nullable)
  - Must be created manually via admin or API with proper department assignment
  
- **For ADMIN role**: No profile is created (as expected)

#### `save_user_profile`
- Ensures profile changes are persisted when user is saved
- Only saves if profile exists

### 2. Updated `users/apps.py`

Added the `ready()` method to `UsersConfig` class:

```python
class UsersConfig(AppConfig):
    name = 'users'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered and will be triggered.
        """
        import users.signals  # noqa: F401
```

The `ready()` method is called by Django when the app is loaded, ensuring signals are registered.

### 3. Updated `settings.py`

Changed the users app registration from:
```python
'users',
```

To:
```python
'users.apps.UsersConfig',  # Use full config path to ensure ready() is called
```

This explicitly uses the UsersConfig class, guaranteeing the `ready()` method is executed.

## How It Works

1. When Django starts, it loads all apps in `INSTALLED_APPS`
2. For `users.apps.UsersConfig`, Django calls the `ready()` method
3. The `ready()` method imports `users.signals`, registering all signal handlers
4. When a new `CustomUser` is created:
   - The `post_save` signal is triggered
   - `create_user_profile` handler checks the user's role
   - If role is `STUDENT`, a `StudentProfile` is automatically created
   - If role is `FACULTY`, no profile is created (requires manual creation with department)
   - If role is `ADMIN`, no profile is created

## Usage Examples

### Student User Creation
```python
from users.models import CustomUser

# Create a student user
student = CustomUser.objects.create_user(
    username='john_doe',
    password='secure_password',
    role='STUDENT',
    email='john@example.com'
)

# StudentProfile is automatically created!
print(student.student_profile.enrollment_number)  # Output: TEMP_1
print(student.student_profile.batch_year)  # Output: 2026

# Update the temporary values
student.student_profile.enrollment_number = '2026CS001'
student.student_profile.batch_year = 2026
student.student_profile.save()
```

### Faculty User Creation
```python
from users.models import CustomUser, FacultyProfile
from academics.models import Department

# Create a faculty user
faculty = CustomUser.objects.create_user(
    username='prof_smith',
    password='secure_password',
    role='FACULTY',
    email='smith@example.com'
)

# FacultyProfile is NOT automatically created (department required)
# Must create manually:
dept = Department.objects.get(code='CS')
FacultyProfile.objects.create(
    user=faculty,
    employee_id='FAC2026001',
    department=dept,
    designation='Professor'
)
```

### Admin User Creation
```python
from users.models import CustomUser

# Create an admin user
admin = CustomUser.objects.create_user(
    username='admin',
    password='secure_password',
    role='ADMIN',
    email='admin@example.com'
)

# No profile is created for admin users
print(hasattr(admin, 'student_profile'))  # Output: False
print(hasattr(admin, 'faculty_profile'))  # Output: False
```

## Important Notes

1. **StudentProfile Auto-Creation**: Works automatically but creates temporary values that should be updated
2. **FacultyProfile Manual Creation**: Requires manual creation because department is mandatory
3. **Signal Registration**: Signals are only active after Django loads the app and calls `ready()`
4. **Testing**: Restart the Django server after making signal changes to ensure they're loaded

## Files Modified

- ✅ `users/signals.py` - Created with signal handlers
- ✅ `users/apps.py` - Added `ready()` method to register signals
- ✅ `academic_erp_project/settings.py` - Updated to use full app config path

## Next Steps

When creating users via API or admin:
1. For students: Update the temporary `enrollment_number` and `batch_year` after creation
2. For faculty: Create the `FacultyProfile` manually with proper department assignment
3. Consider adding validation to ensure profiles exist before allowing certain operations
