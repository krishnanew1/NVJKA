# Faculty Models Documentation

## Overview

Created the ClassAssignment model in the `faculty` app to manage faculty teaching assignments, linking faculty members to subjects they teach in specific semesters and academic years.

## Model: ClassAssignment

**Purpose:** Links FacultyProfile to Subject with semester and academic year tracking.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `faculty` | ForeignKey | Link to FacultyProfile | CASCADE delete, required |
| `subject` | ForeignKey | Link to Subject (from academics) | CASCADE delete, required |
| `semester` | IntegerField | Semester number | Min: 1, required |
| `academic_year` | CharField | Academic year | Max length: 10, required |
| `section` | CharField | Section/class group | Max length: 10, optional |
| `max_students` | IntegerField | Maximum class capacity | Min: 1, optional |
| `is_active` | BooleanField | Assignment status | Default: True |
| `created_at` | DateTimeField | Record creation timestamp | Auto-set |
| `updated_at` | DateTimeField | Last update timestamp | Auto-update |

### Constraints

**Unique Together:** `(faculty, subject, semester, academic_year, section)`
- Prevents duplicate assignments for the same faculty-subject-semester-year-section combination
- Allows same faculty to teach same subject in different sections or semesters

**Ordering:** Most recent first (`-academic_year`, `-semester`, `subject__name`)

### Related Names

- `faculty.class_assignments` - Access all assignments for a faculty member
- `subject.class_assignments` - Access all assignments for a subject

### String Representation

```python
"Jane Smith - CS101 - 2025-2026 Sem 1 (A)"
"FAC2026001 - MATH201 - 2026 Sem 2"
```

### Methods

#### `get_enrolled_count()`
Returns the number of students enrolled in this class.
- Currently returns 0 (placeholder)
- Future implementation will query Enrollment model

#### `is_full()`
Checks if the class has reached maximum capacity.
- Returns `False` if `max_students` is None (unlimited)
- Returns `True` if enrolled count >= max_students

---

## Use Cases

### 1. Faculty Teaching Assignment

Assign a faculty member to teach a subject in a specific semester:

```python
from faculty.models import ClassAssignment
from users.models import FacultyProfile
from academics.models import Subject

# Get faculty and subject
faculty = FacultyProfile.objects.get(employee_id='FAC2026001')
subject = Subject.objects.get(code='CS101')

# Create assignment
assignment = ClassAssignment.objects.create(
    faculty=faculty,
    subject=subject,
    semester=1,
    academic_year='2025-2026',
    section='A',
    max_students=40,
    is_active=True
)
```

### 2. Multiple Sections

Same faculty teaching multiple sections of the same subject:

```python
# Section A
ClassAssignment.objects.create(
    faculty=faculty,
    subject=subject,
    semester=1,
    academic_year='2025-2026',
    section='A',
    max_students=40
)

# Section B
ClassAssignment.objects.create(
    faculty=faculty,
    subject=subject,
    semester=1,
    academic_year='2025-2026',
    section='B',
    max_students=40
)
```

### 3. Query Faculty Assignments

Get all active assignments for a faculty member:

```python
# Get faculty's current assignments
active_assignments = faculty.class_assignments.filter(is_active=True)

# Get assignments for specific semester
semester_1_assignments = faculty.class_assignments.filter(
    semester=1,
    academic_year='2025-2026'
)

# Get all subjects taught by faculty
subjects_taught = Subject.objects.filter(
    class_assignments__faculty=faculty,
    class_assignments__is_active=True
).distinct()
```

### 4. Query Subject Assignments

Get all faculty teaching a subject:

```python
# Get all faculty teaching CS101
cs101_faculty = FacultyProfile.objects.filter(
    class_assignments__subject__code='CS101',
    class_assignments__is_active=True
).distinct()

# Get current semester assignments for a subject
current_assignments = subject.class_assignments.filter(
    semester=1,
    academic_year='2025-2026',
    is_active=True
)
```

### 5. Check Class Capacity

```python
assignment = ClassAssignment.objects.get(id=1)

# Check if class is full
if assignment.is_full():
    print("Class is at maximum capacity")
else:
    available_seats = assignment.max_students - assignment.get_enrolled_count()
    print(f"Available seats: {available_seats}")
```

---

## Admin Configuration

### Features

- **List Display:** Faculty name, employee ID, subject name/code, semester, year, section, capacity, status
- **Filters:** Academic year, semester, active status, department
- **Search:** Faculty details, subject details, academic year, section
- **Raw ID Fields:** Faculty and subject (for better performance)
- **Organized Fieldsets:** Assignment info, class settings, timestamps
- **Custom Methods:** Display related data from foreign keys

### Admin Interface

Access at: `http://127.0.0.1:8000/admin/faculty/classassignment/`

---

## Database Schema

### Table: `faculty_classassignment`

```sql
CREATE TABLE faculty_classassignment (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    faculty_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    semester INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    section VARCHAR(10) NULL,
    max_students INT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES users_facultyprofile(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES academics_subject(id) ON DELETE CASCADE,
    UNIQUE KEY (faculty_id, subject_id, semester, academic_year, section),
    CHECK (semester >= 1),
    CHECK (max_students >= 1 OR max_students IS NULL)
);
```

---

## Example Scenarios

### Scenario 1: Semester Course Planning

```python
# Assign faculty for Fall 2025 semester
assignments = [
    {
        'faculty': prof_smith,
        'subject': cs101,
        'semester': 1,
        'academic_year': '2025-2026',
        'section': 'A',
        'max_students': 40
    },
    {
        'faculty': prof_jones,
        'subject': cs201,
        'semester': 1,
        'academic_year': '2025-2026',
        'section': 'A',
        'max_students': 35
    }
]

for assignment_data in assignments:
    ClassAssignment.objects.create(**assignment_data)
```

### Scenario 2: Faculty Workload Report

```python
# Get faculty workload for a semester
faculty = FacultyProfile.objects.get(employee_id='FAC2026001')
assignments = faculty.class_assignments.filter(
    semester=1,
    academic_year='2025-2026',
    is_active=True
)

print(f"Faculty: {faculty.user.get_full_name()}")
print(f"Total Classes: {assignments.count()}")
for assignment in assignments:
    print(f"  - {assignment.subject.code} ({assignment.section})")
```

### Scenario 3: Subject Coverage Check

```python
# Check if all subjects have faculty assigned
from academics.models import Subject

subjects = Subject.objects.filter(semester=1)
for subject in subjects:
    assignments = subject.class_assignments.filter(
        semester=1,
        academic_year='2025-2026',
        is_active=True
    )
    
    if not assignments.exists():
        print(f"WARNING: {subject.code} has no faculty assigned")
    else:
        faculty_list = [a.faculty.user.get_full_name() for a in assignments]
        print(f"{subject.code}: {', '.join(faculty_list)}")
```

### Scenario 4: Deactivate Past Assignments

```python
# Deactivate assignments from previous academic year
ClassAssignment.objects.filter(
    academic_year='2024-2025',
    is_active=True
).update(is_active=False)
```

---

## Integration with Other Models

### With FacultyProfile (users app)
- Faculty can have multiple class assignments
- Access via `faculty.class_assignments.all()`

### With Subject (academics app)
- Subject can be taught by multiple faculty (different sections/semesters)
- Access via `subject.class_assignments.all()`

### Future Integration with Enrollment (students app)
- Students enroll in specific class assignments
- Track enrollment count per assignment
- Enforce max_students capacity

---

## API Integration (Future)

Potential API endpoints:

**Faculty Endpoints:**
- `GET /api/faculty/assignments/` - List faculty's assignments
- `GET /api/faculty/assignments/{id}/` - Get assignment details
- `GET /api/faculty/assignments/{id}/students/` - List enrolled students

**Admin Endpoints:**
- `POST /api/faculty/assignments/` - Create assignment (admin only)
- `PUT /api/faculty/assignments/{id}/` - Update assignment (admin only)
- `DELETE /api/faculty/assignments/{id}/` - Delete assignment (admin only)
- `GET /api/faculty/workload/` - Faculty workload report (admin only)

**Student Endpoints:**
- `GET /api/students/available-classes/` - List available classes with capacity

---

## Validation Rules

1. **Semester:** Must be >= 1
2. **Max Students:** Must be >= 1 or NULL (unlimited)
3. **Unique Assignment:** Same faculty cannot be assigned to same subject-semester-year-section twice
4. **Active Status:** Can be toggled to deactivate old assignments
5. **Section:** Optional, allows multiple sections of same subject

---

## Migrations

**Created:**
- `faculty/migrations/0001_initial.py` - Creates ClassAssignment table

**Applied:** ✅ Successfully migrated to database

---

## Files Created/Modified

- ✅ `faculty/models.py` - Created ClassAssignment model
- ✅ `faculty/admin.py` - Registered model with comprehensive admin config
- ✅ `faculty/migrations/0001_initial.py` - Database migration
- ✅ Database table created: `faculty_classassignment`

---

## Testing Recommendations

Create tests for:
1. ClassAssignment creation with all fields
2. Unique constraint validation (duplicate assignments)
3. Multiple sections for same subject
4. Faculty workload queries
5. Subject coverage queries
6. Capacity checking (is_full method)
7. Active/inactive status filtering
8. Semester and year filtering
9. Related queries (faculty.class_assignments, subject.class_assignments)

---

## Next Steps

1. Create serializers for ClassAssignment
2. Create API endpoints for assignment management
3. Integrate with Enrollment model for capacity tracking
4. Add prerequisite checking for assignments
5. Create faculty workload reports
6. Add conflict detection (same faculty, same time slot)
7. Create student class selection interface
8. Add assignment approval workflow

---

## Benefits

1. **Organized Teaching Assignments:** Clear tracking of who teaches what
2. **Capacity Management:** Control class sizes with max_students
3. **Historical Records:** Track assignments across semesters and years
4. **Multiple Sections:** Support for multiple sections of same subject
5. **Flexible Queries:** Easy to query by faculty, subject, semester, or year
6. **Admin Interface:** User-friendly management through Django admin
7. **Data Integrity:** Unique constraints prevent duplicate assignments
8. **Scalability:** Supports large numbers of faculty and subjects
