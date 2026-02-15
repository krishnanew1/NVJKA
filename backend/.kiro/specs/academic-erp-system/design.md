# Design Document: Institute Academic Management System (ERP)

## Overview

The Institute Academic Management System is a headless Django-based platform that provides comprehensive RESTful APIs for educational institute management. The system follows a modular architecture with seven distinct Django apps, each handling specific domain functionality. The backend uses Django REST Framework (DRF) for API development, MySQL for data persistence, and JWT/Token authentication for security.

The system serves three primary user roles through role-based API access: Academic Administrators (full system access), Faculty (course and student management), and Students (self-service academic information). The decoupled architecture allows for flexible frontend implementations using modern frameworks like React.js.

## Architecture

### System Architecture

The system follows a three-tier architecture:

1. **Presentation Layer**: Decoupled frontend (React.js or other modern frameworks)
2. **API Layer**: Django REST Framework providing RESTful endpoints
3. **Data Layer**: MySQL database with Django ORM

### Modular App Structure

The Django project is organized into seven specialized apps:

```
academic_erp/
├── users/          # Custom user model and authentication
├── academics/      # Departments, courses, subjects, timetables
├── students/       # Student profiles and enrollment management
├── faculty/        # Faculty profiles and course assignments
├── attendance/     # Daily attendance tracking
├── exams/          # Assessments, marks, and grades
└── communication/  # Notices, announcements, feedback
```

### API Design Principles

- RESTful endpoint design following HTTP conventions
- Consistent JSON response format across all endpoints
- Role-based access control at the endpoint level
- Proper HTTP status codes for all responses
- Comprehensive error handling and validation

## Components and Interfaces

### Authentication Component

**JWT Authentication Service**
- Handles user login and token generation
- Validates tokens on each API request
- Manages token refresh and expiration
- Implements role-based permissions

**API Endpoints:**
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

### User Management Component (users app)

**CustomUser Model**
- Extends Django's AbstractUser
- Includes role field (Academic_Admin, Faculty, Student)
- Additional fields: profile_picture, phone_number, address
- Handles user creation and profile management

**API Endpoints:**
- `GET /api/users/profile/` - Get current user profile
- `PUT /api/users/profile/` - Update user profile
- `POST /api/users/change-password/` - Change password

### Academic Structure Component (academics app)

**Models:**
- Department: Manages academic departments
- Course: Defines courses with codes, names, credits
- Subject: Links courses to specific semesters
- Timetable: Manages class schedules

**API Endpoints:**
- `GET /api/academics/departments/` - List departments
- `GET /api/academics/courses/` - List courses
- `GET /api/academics/timetable/` - Get timetable data
- `POST /api/academics/courses/` - Create course (Admin only)

### Student Management Component (students app)

**StudentProfile Model**
- Links to CustomUser with OneToOne relationship
- Includes enrollment_number, department, academic_year
- Manages student-specific data and enrollment

**API Endpoints:**
- `GET /api/students/dashboard/` - Student dashboard data
- `GET /api/students/enrollment/` - Current enrollments
- `POST /api/students/enroll/` - Enroll in course
- `GET /api/students/academic-history/` - Academic records

### Faculty Management Component (faculty app)

**FacultyProfile Model**
- Links to CustomUser with OneToOne relationship
- Includes designation, department, specialization
- Manages faculty-specific data and course assignments

**API Endpoints:**
- `GET /api/faculty/dashboard/` - Faculty dashboard data
- `GET /api/faculty/classes/` - Assigned classes
- `GET /api/faculty/students/{class_id}/` - Class roster
- `POST /api/faculty/resources/` - Upload learning resources

### Attendance Management Component (attendance app)

**Attendance Model**
- Tracks daily attendance with date, status, student, class
- Supports Present, Absent, Late status types
- Links to student and class for proper tracking

**API Endpoints:**
- `GET /api/attendance/class/{class_id}/` - Get class attendance
- `POST /api/attendance/mark/` - Mark attendance
- `GET /api/attendance/student/{student_id}/` - Student attendance history
- `GET /api/attendance/reports/` - Attendance reports

### Examination and Grading Component (exams app)

**Models:**
- Assessment: Defines exams, assignments, quizzes
- Grade: Stores individual student grades
- AcademicRecord: Comprehensive academic performance

**API Endpoints:**
- `GET /api/exams/assessments/` - List assessments
- `POST /api/exams/grades/` - Submit grades
- `GET /api/exams/student-grades/{student_id}/` - Student grades
- `GET /api/exams/transcripts/{student_id}/` - Generate transcript

### Communication Component (communication app)

**Models:**
- Notice: System-wide announcements
- Announcement: Class-specific announcements
- LearningResource: File uploads for courses
- AnonymousFeedback: Student feedback system

**API Endpoints:**
- `GET /api/communication/notices/` - Get notices
- `POST /api/communication/announcements/` - Create announcement
- `GET /api/communication/resources/{course_id}/` - Course resources
- `POST /api/communication/feedback/` - Submit anonymous feedback

## Data Models

### Core User Model

```python
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('academic_admin', 'Academic Administrator'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
```

### Academic Structure Models

```python
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    prerequisites = models.ManyToManyField('self', blank=True)

class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=10)
    faculty = models.ForeignKey('faculty.FacultyProfile', on_delete=models.SET_NULL, null=True)
```

### Profile Models

```python
class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    enrollment_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=10)
    date_of_admission = models.DateField()

class FacultyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=200)
```

### Academic Records and Attendance

```python
class AcademicRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=5)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=10)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
```

### Communication Models

```python
class LearningResource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='resources/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

class AnonymousFeedback(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)
```
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User Model Structure Validation
*For any* CustomUser instance, it should extend AbstractUser and contain role, profile_picture, phone_number, and address fields with proper field types and constraints.
**Validates: Requirements 1.1, 5.2**

### Property 2: Authentication Token Generation
*For any* valid user credentials, successful authentication should return a valid JWT/DRF token that can be used for subsequent API requests.
**Validates: Requirements 1.2, 12.2**

### Property 3: Role-Based Dashboard Access
*For any* authenticated user, the dashboard API should return data appropriate to their specific role (Student, Faculty, or Academic_Admin).
**Validates: Requirements 1.3, 2.1, 3.1**

### Property 4: Role-Based Endpoint Access Control
*For any* API endpoint and user role combination, users should only be able to access endpoints appropriate to their role, with unauthorized access properly denied.
**Validates: Requirements 1.5, 12.4, 9.2**

### Property 5: Student Enrollment Validation
*For any* student enrollment attempt, the system should validate prerequisites, enrollment limits, and academic session availability before allowing registration.
**Validates: Requirements 2.2, 2.5, 8.4, 8.5**

### Property 6: Academic Data Retrieval Completeness
*For any* student requesting academic history, the API should return complete and accurate grades, attendance records, and course completion data.
**Validates: Requirements 2.3, 2.4**

### Property 7: Faculty Class Management
*For any* faculty member, they should be able to access only their assigned classes and perform attendance marking and grade entry for students in those classes.
**Validates: Requirements 3.1, 3.2, 3.3, 6.1, 6.2**

### Property 8: Attendance Record Persistence
*For any* attendance marking operation, the system should store complete attendance records with date, status, student, and class information.
**Validates: Requirements 3.2, 6.3**

### Property 9: Administrative CRUD Operations
*For any* Academic_Admin user, they should be able to create, read, update, and delete academic sessions, departments, courses, and user assignments.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 10: Data Integrity Maintenance
*For any* data modification operation, the system should maintain referential integrity and cascade updates to related records appropriately.
**Validates: Requirements 4.5, 5.4**

### Property 11: Model Relationship Validation
*For any* model instance creation, all required foreign key relationships should be properly established and validated across apps.
**Validates: Requirements 5.3, 11.3**

### Property 12: Attendance Calculation Accuracy
*For any* student and class combination, attendance percentage calculations should be mathematically correct based on present/total class sessions.
**Validates: Requirements 6.4**

### Property 13: Grade Validation and GPA Calculation
*For any* grade entry, the system should validate grade ranges and automatically calculate accurate cumulative and semester GPAs based on credits and grades.
**Validates: Requirements 7.1, 7.2, 7.3**

### Property 14: Academic Record Audit Trail
*For any* grade modification, the system should maintain a complete history of changes while preserving the current academic record.
**Validates: Requirements 7.4**

### Property 15: Schedule Conflict Prevention
*For any* class scheduling operation, the system should detect and prevent faculty schedule conflicts and classroom double-booking.
**Validates: Requirements 8.1, 8.2**

### Property 16: Security and Authentication Enforcement
*For any* API request, the system should validate authentication tokens, reject invalid/expired tokens, and return appropriate HTTP status codes for unauthorized access.
**Validates: Requirements 9.2, 9.5, 12.3, 12.5**

### Property 17: Audit Logging Completeness
*For any* critical operation (grade changes, user creation, administrative actions), the system should generate appropriate audit log entries.
**Validates: Requirements 9.3**

### Property 18: Password Security
*For any* user password, it should be properly hashed using Django's built-in password hashing and never stored in plain text.
**Validates: Requirements 9.4**

### Property 19: File Upload and Resource Management
*For any* faculty member uploading learning resources, the files should be properly stored and associated with the correct course and faculty.
**Validates: Requirements 13.1**

### Property 20: Anonymous Feedback System
*For any* student feedback submission, the data should be properly anonymized while maintaining course and faculty associations for reporting.
**Validates: Requirements 13.3, 13.4, 13.5**

## Error Handling

### API Error Response Format

All API endpoints follow a consistent error response format:

```json
{
    "error": true,
    "message": "Human-readable error description",
    "code": "ERROR_CODE",
    "details": {
        "field_errors": {},
        "validation_errors": []
    }
}
```

### Error Categories

**Authentication Errors (401)**
- Invalid credentials
- Expired tokens
- Missing authentication headers

**Authorization Errors (403)**
- Insufficient role permissions
- Access to unauthorized resources
- Role-based restrictions

**Validation Errors (400)**
- Invalid input data
- Missing required fields
- Constraint violations
- Business rule violations

**Not Found Errors (404)**
- Non-existent resources
- Invalid resource IDs
- Deleted or archived records

**Conflict Errors (409)**
- Duplicate enrollment attempts
- Schedule conflicts
- Capacity limit violations

**Server Errors (500)**
- Database connection issues
- Unexpected system failures
- Third-party service failures

### Error Handling Strategies

**Input Validation**
- Use Django REST Framework serializers for comprehensive input validation
- Implement custom validators for business rules
- Provide detailed field-level error messages

**Database Error Handling**
- Handle foreign key constraint violations gracefully
- Manage transaction rollbacks for data consistency
- Provide meaningful error messages for constraint violations

**File Upload Error Handling**
- Validate file types and sizes
- Handle storage failures gracefully
- Provide progress feedback for large uploads

## Testing Strategy

### Dual Testing Approach

The system employs both unit testing and property-based testing for comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points between components. Unit tests validate concrete scenarios and ensure individual components work correctly in isolation.

**Property Tests**: Verify universal properties across all inputs through randomized testing. Property tests ensure that business rules and system invariants hold true across the entire input space.

### Property-Based Testing Configuration

- **Testing Library**: Use Hypothesis for Python property-based testing
- **Test Iterations**: Minimum 100 iterations per property test to ensure comprehensive coverage
- **Test Tagging**: Each property test references its corresponding design document property
- **Tag Format**: `# Feature: academic-erp-system, Property {number}: {property_text}`

### Unit Testing Focus Areas

**Authentication and Authorization**
- Test specific login scenarios with valid/invalid credentials
- Test role-based access with concrete user examples
- Test token expiration and refresh mechanisms

**API Endpoint Integration**
- Test API request/response formats
- Test HTTP status code accuracy
- Test cross-app model relationships

**Business Logic Edge Cases**
- Test enrollment capacity limits
- Test prerequisite validation edge cases
- Test GPA calculation boundary conditions

**File Upload and Storage**
- Test various file types and sizes
- Test storage failure scenarios
- Test file access permissions

### Property Test Implementation

Each correctness property must be implemented as a single property-based test that:
1. Generates random valid inputs using Hypothesis strategies
2. Executes the system operation
3. Verifies the property holds true for all generated inputs
4. References the specific design document property in comments

### Test Data Management

**Test Database**
- Use separate test database for all testing
- Implement database fixtures for consistent test data
- Use factory patterns for generating test objects

**Test User Management**
- Create test users for each role type
- Use consistent test credentials across test suites
- Implement user cleanup after test execution

### Continuous Integration

**Automated Testing**
- Run all tests on every code commit
- Include both unit and property tests in CI pipeline
- Maintain minimum test coverage thresholds

**Performance Testing**
- Monitor API response times
- Test database query performance
- Validate system behavior under load