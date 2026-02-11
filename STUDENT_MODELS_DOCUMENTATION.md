# Student Models Documentation

## Overview

Created two models in the `students` app to manage student enrollments and academic history.

## Models Created

### 1. Enrollment Model

**Purpose:** Tracks student course registrations with enrollment status.

**Fields:**

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `student` | ForeignKey | Link to StudentProfile | CASCADE delete, required |
| `course` | ForeignKey | Link to Course | CASCADE delete, required |
| `date_enrolled` | DateField | Enrollment date | Auto-set on creation |
| `status` | CharField | Enrollment status | Choices: ENROLLED, COMPLETED, DROPPED, WITHDRAWN |
| `created_at` | DateTimeField | Record creation timestamp | Auto-set |
| `updated_at` | DateTimeField | Last update timestamp | Auto-update |

**Status Choices:**
- `ENROLLED` - Currently enrolled (default)
- `COMPLETED` - Course completed
- `DROPPED` - Dropped before completion
- `WITHDRAWN` - Withdrawn from course

**Constraints:**
- Unique together: `(student, course)` - A student can only enroll in a course once
- Ordering: Most recent enrollments first (`-date_enrolled`)

**Related Names:**
- `student.enrollments` - Access all enrollments for a student
- `course.enrollments` - Access all enrollments for a course

**String Representation:**
```python
"2026CS001 - CS101 (ENROLLED)"
```

**Example Usage:**
```python
from students.models import Enrollment
from users.models import StudentProfile
from academics.models import Course

# Get student and course
student = StudentProfile.objects.get(enrollment_number='2026CS001')
course = Course.objects.get(code='CS101')

# Create enrollment
enrollment = Enrollment.objects.create(
    student=student,
    course=course,
    status='ENROLLED'
)

# Access enrollments
student_courses = student.enrollments.all()
course_students = course.enrollments.filter(status='ENROLLED')

# Update status
enrollment.status = 'COMPLETED'
enrollment.save()
```

---

### 2. AcademicHistory Model

**Purpose:** Stores student's previous academic records with flexible JSON grade data.

**Fields:**

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `student` | ForeignKey | Link to StudentProfile | CASCADE delete, required |
| `previous_grades` | JSONField | Flexible grade data | Default: empty dict |
| `year_completed` | IntegerField | Academic year | Min: 1900, required |
| `semester` | IntegerField | Semester number | Min: 1, optional |
| `gpa` | DecimalField | GPA for period | Max digits: 4, decimals: 2, min: 0.0, optional |
| `remarks` | TextField | Additional notes | Optional |
| `created_at` | DateTimeField | Record creation timestamp | Auto-set |
| `updated_at` | DateTimeField | Last update timestamp | Auto-update |

**Constraints:**
- Unique together: `(student, year_completed, semester)` - One record per student per period
- Ordering: Most recent first (`-year_completed`, `-semester`)

**Related Names:**
- `student.academic_history` - Access all academic history for a student

**String Representation:**
```python
"2026CS001 - 2025 Sem 1"
"2026CS001 - 2025"  # If no semester specified
```

**JSON Grade Data Structure (Example):**
```json
{
  "courses": [
    {
      "code": "CS101",
      "name": "Introduction to Programming",
      "grade": "A",
      "credits": 4,
      "marks": 95
    },
    {
      "code": "MATH201",
      "name": "Calculus II",
      "grade": "B+",
      "credits": 3,
      "marks": 87
    }
  ],
  "total_credits": 7,
  "semester_gpa": 3.85,
  "cumulative_gpa": 3.75
}
```

**Example Usage:**
```python
from students.models import AcademicHistory
from users.models import StudentProfile

# Get student
student = StudentProfile.objects.get(enrollment_number='2026CS001')

# Create academic history
history = AcademicHistory.objects.create(
    student=student,
    year_completed=2025,
    semester=1,
    gpa=3.85,
    previous_grades={
        "courses": [
            {
                "code": "CS101",
                "name": "Introduction to Programming",
                "grade": "A",
                "credits": 4,
                "marks": 95
            }
        ],
        "total_credits": 4,
        "semester_gpa": 3.85
    },
    remarks="Excellent performance"
)

# Access history
student_history = student.academic_history.all()
recent_history = student.academic_history.first()  # Most recent

# Query by year
year_2025 = student.academic_history.filter(year_completed=2025)
```

---

## Admin Configuration

Both models are registered in Django admin with comprehensive configurations.

### Enrollment Admin Features:
- List display: Student name, enrollment number, course name, course code, status, date
- Filters: Status, date enrolled, department
- Search: Student details, course details
- Raw ID fields for better performance
- Date hierarchy for easy navigation
- Custom methods to display related data

### AcademicHistory Admin Features:
- List display: Student name, enrollment number, year, semester, GPA
- Filters: Year completed, semester
- Search: Student details, year
- Raw ID fields for better performance
- Organized fieldsets for better UX
- Custom methods to display related data

---

## Database Schema

### Enrollment Table: `students_enrollment`
```sql
CREATE TABLE students_enrollment (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    date_enrolled DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ENROLLED',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_studentprofile(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES academics_course(id) ON DELETE CASCADE,
    UNIQUE KEY (student_id, course_id)
);
```

### AcademicHistory Table: `students_academichistory`
```sql
CREATE TABLE students_academichistory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    previous_grades JSON NOT NULL,
    year_completed INT NOT NULL,
    semester INT NULL,
    gpa DECIMAL(4,2) NULL,
    remarks TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_studentprofile(id) ON DELETE CASCADE,
    UNIQUE KEY (student_id, year_completed, semester)
);
```

---

## Migrations

**Created:**
- `students/migrations/0001_initial.py` - Creates Enrollment and AcademicHistory tables
- `users/migrations/0004_alter_customuser_id_alter_facultyprofile_id_and_more.py` - Auto-field updates

**Applied:** ✅ Successfully migrated to database

---

## Use Cases

### Enrollment Management
1. **Course Registration:** Create enrollment when student registers
2. **Track Progress:** Update status as student progresses
3. **Course Completion:** Mark as COMPLETED when finished
4. **Withdrawal Handling:** Mark as DROPPED or WITHDRAWN if needed
5. **Enrollment Reports:** Query by status, date, department

### Academic History Tracking
1. **Semester Records:** Store grades for each semester
2. **GPA Tracking:** Record semester and cumulative GPA
3. **Transcript Generation:** Retrieve all academic history
4. **Performance Analysis:** Query by year, semester, GPA
5. **Flexible Data:** Store any grade-related data in JSON

---

## API Integration (Future)

These models are ready for API integration with serializers and viewsets:

**Potential Endpoints:**
- `GET /api/students/enrollments/` - List student's enrollments
- `POST /api/students/enrollments/` - Create new enrollment
- `PATCH /api/students/enrollments/{id}/` - Update enrollment status
- `GET /api/students/academic-history/` - List academic history
- `POST /api/students/academic-history/` - Add academic record
- `GET /api/students/transcript/` - Generate full transcript

---

## Files Created/Modified

- ✅ `students/models.py` - Created Enrollment and AcademicHistory models
- ✅ `students/admin.py` - Registered models with comprehensive admin config
- ✅ `students/migrations/0001_initial.py` - Database migration
- ✅ Database tables created and ready

---

## Testing Recommendations

Create tests for:
1. Enrollment creation and unique constraint
2. Status transitions (ENROLLED → COMPLETED)
3. Academic history with JSON data
4. Unique constraint for academic history
5. Related queries (student.enrollments, student.academic_history)
6. GPA validation (>= 0.0)
7. Year validation (>= 1900)

---

## Next Steps

1. Create serializers for Enrollment and AcademicHistory
2. Create API endpoints for enrollment management
3. Create API endpoints for academic history
4. Add enrollment validation (prerequisites, capacity)
5. Add GPA calculation utilities
6. Create transcript generation functionality
