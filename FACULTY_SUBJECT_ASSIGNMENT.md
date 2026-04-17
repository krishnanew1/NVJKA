# Faculty-Subject Assignment System

## Overview

This document describes the faculty-subject assignment system that allows administrators to assign faculty members to subjects. The system includes database models, API endpoints, and seeded test data.

## Database Schema

### Subject Model Enhancement

The `Subject` model in `backend/apps/academics/models.py` now includes a `faculty` field:

```python
faculty = models.ForeignKey(
    'users.FacultyProfile',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assigned_subjects',
    help_text="Faculty member assigned to teach this subject"
)
```

**Key Features:**
- Optional assignment (null=True, blank=True)
- SET_NULL on delete (preserves subject if faculty is deleted)
- Reverse relation: `faculty.assigned_subjects.all()`

### Migration

**File:** `backend/apps/academics/migrations/0006_subject_faculty.py`

Applied successfully to add the faculty field to existing subjects.

## Seeded Data

### Management Command

**File:** `backend/apps/academics/management/commands/seed_real_data.py`

**Usage:**
```bash
python manage.py seed_real_data
```

### Created Data

#### Subjects (4 total)
1. **Multivariate Data Analysis** (CS401)
   - Semester 4, 4 credits
   - Auto-assigned to: Ajay Kumar (FAC101)

2. **Operating Systems** (CS301)
   - Semester 3, 4 credits
   - Auto-assigned to: Deepak Kumar Dewangan (FAC102)

3. **Advanced Numerical Methods** (CS402)
   - Semester 4, 4 credits
   - Auto-assigned to: Anuraj Singh (FAC103)

4. **Software Engineering** (CS302)
   - Semester 3, 4 credits
   - Auto-assigned to: Anurag Srivastav (FAC104)

#### Faculty Members (4 total)

| Username | Password | Name | Employee ID | Designation |
|----------|----------|------|-------------|-------------|
| ajay_k | faculty123 | Ajay Kumar | FAC101 | Associate Professor |
| deepak_d | faculty123 | Deepak Kumar Dewangan | FAC102 | Assistant Professor |
| anuraj_s | faculty123 | Anuraj Singh | FAC103 | Assistant Professor |
| anurag_s | faculty123 | Anurag Srivastav | FAC104 | Associate Professor |

**Note:** All faculty accounts use the password `faculty123` for testing.

## API Endpoints

### 1. Assign Faculty to Subject

**Endpoint:** `PATCH /api/academics/subjects/{id}/assign-faculty/`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "faculty_id": 5
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Faculty John Smith assigned to Operating Systems",
  "data": {
    "id": 1,
    "name": "Operating Systems",
    "code": "CS301",
    "course": {
      "id": 1,
      "name": "Bachelor of Technology in Computer Science",
      "code": "BTCS"
    },
    "faculty_info": {
      "id": 5,
      "employee_id": "FAC102",
      "name": "Deepak Kumar Dewangan",
      "designation": "Assistant Professor"
    },
    "semester": 3,
    "credits": 4
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Faculty with ID 999 not found",
  "code": 404
}
```

### 2. Unassign Faculty from Subject

**Endpoint:** `PATCH /api/academics/subjects/{id}/assign-faculty/`

**Request Body:**
```json
{
  "faculty_id": null
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Faculty unassigned successfully",
  "data": {
    "id": 1,
    "name": "Operating Systems",
    "code": "CS301",
    "faculty_info": null
  }
}
```

### 3. Get Subject with Faculty Info

**Endpoint:** `GET /api/academics/subjects/{id}/`

**Response:**
```json
{
  "id": 1,
  "name": "Operating Systems",
  "code": "CS301",
  "course": {
    "id": 1,
    "name": "Bachelor of Technology in Computer Science",
    "code": "BTCS",
    "department": {
      "id": 1,
      "name": "Computer Science",
      "code": "CS"
    }
  },
  "faculty_info": {
    "id": 5,
    "employee_id": "FAC102",
    "name": "Deepak Kumar Dewangan",
    "designation": "Assistant Professor"
  },
  "semester": 3,
  "semester_display": "Semester 3",
  "credits": 4,
  "is_mandatory": true
}
```

### 4. List All Subjects with Faculty Info

**Endpoint:** `GET /api/academics/subjects/`

**Query Parameters:**
- `faculty={faculty_id}` - Filter by assigned faculty
- `course={course_id}` - Filter by course
- `semester={1-10}` - Filter by semester

**Response:**
```json
[
  {
    "id": 1,
    "name": "Operating Systems",
    "code": "CS301",
    "faculty_info": {
      "id": 5,
      "employee_id": "FAC102",
      "name": "Deepak Kumar Dewangan",
      "designation": "Assistant Professor"
    }
  },
  {
    "id": 2,
    "name": "Database Systems",
    "code": "CS302",
    "faculty_info": null
  }
]
```

## Serializer Updates

### SubjectSerializer

**File:** `backend/apps/academics/serializers.py`

**New Fields:**
- `faculty_info` (SerializerMethodField, read-only) - Complete faculty details
- `faculty_id` (IntegerField, write-only) - For assignment operations

**Faculty Info Structure:**
```python
{
    'id': 5,
    'employee_id': 'FAC102',
    'name': 'Deepak Kumar Dewangan',
    'designation': 'Assistant Professor'
}
```

**Validation:**
- Validates faculty_id exists before assignment
- Allows null to unassign faculty
- Returns None if no faculty assigned

## Testing

### Test Scripts

#### 1. Model and Serializer Test
**File:** `backend/test_faculty_assignment.py`

Tests:
- Listing subjects with faculty information
- Assigning faculty to subjects
- Unassigning faculty from subjects
- Serializer output validation

**Run:**
```bash
cd backend
python test_faculty_assignment.py
```

#### 2. API Endpoint Test
**File:** `backend/test_faculty_api.py`

Tests:
- POST assign faculty endpoint
- PATCH unassign faculty endpoint
- GET subject with faculty info
- GET list subjects with faculty filter

**Run:**
```bash
cd backend
python test_faculty_api.py
```

### Expected Output

Both test scripts should complete successfully with output showing:
- ✓ Faculty assigned successfully
- ✓ Faculty information displayed correctly
- ✓ Faculty unassigned successfully
- ✓ API endpoints returning correct data

## Usage Examples

### Python/Django

```python
from apps.academics.models import Subject
from apps.users.models import FacultyProfile

# Get a subject
subject = Subject.objects.get(code='CS301')

# Assign faculty
faculty = FacultyProfile.objects.get(employee_id='FAC102')
subject.faculty = faculty
subject.save()

# Get all subjects taught by a faculty
faculty_subjects = faculty.assigned_subjects.all()

# Unassign faculty
subject.faculty = None
subject.save()
```

### API (JavaScript/React)

```javascript
// Assign faculty to subject
const assignFaculty = async (subjectId, facultyId) => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/academics/subjects/${subjectId}/assign-faculty/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ faculty_id: facultyId })
    }
  );
  return response.json();
};

// Get subject with faculty info
const getSubject = async (subjectId) => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/academics/subjects/${subjectId}/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
};

// List subjects by faculty
const getSubjectsByFaculty = async (facultyId) => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/academics/subjects/?faculty=${facultyId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
};
```

## Frontend Integration (Future)

### Admin Subject Management Page

**Suggested Features:**
1. **Subject List View**
   - Display all subjects with assigned faculty
   - Filter by department, course, semester
   - Search by subject name/code

2. **Faculty Assignment Modal**
   - Dropdown to select faculty member
   - Show faculty details (name, employee ID, designation)
   - Assign/Unassign button

3. **Faculty Workload View**
   - List all faculty members
   - Show number of assigned subjects per faculty
   - Visual indicator for overloaded faculty

4. **Bulk Assignment**
   - Select multiple subjects
   - Assign same faculty to multiple subjects
   - Useful for lab sessions

## Database Queries

### Useful Queries

```python
# Get all subjects without faculty assigned
unassigned_subjects = Subject.objects.filter(faculty__isnull=True)

# Get faculty with most subjects
from django.db.models import Count
faculty_workload = FacultyProfile.objects.annotate(
    subject_count=Count('assigned_subjects')
).order_by('-subject_count')

# Get subjects by department with faculty info
cs_subjects = Subject.objects.filter(
    course__department__code='CS'
).select_related('faculty__user', 'course')

# Get all subjects for a specific semester with faculty
semester_3_subjects = Subject.objects.filter(
    semester=3
).select_related('faculty__user')
```

## Security Considerations

1. **Authorization:**
   - Only Admin users can assign/unassign faculty
   - Faculty can view their assigned subjects
   - Students can view subject faculty information

2. **Validation:**
   - Faculty ID must exist before assignment
   - Null values allowed for unassignment
   - Proper error messages for invalid operations

3. **Data Integrity:**
   - SET_NULL on faculty deletion (preserves subjects)
   - No cascade deletion of subjects
   - Maintains historical data

## Future Enhancements

1. **Assignment History:**
   - Track when faculty was assigned/unassigned
   - Maintain historical records
   - Audit trail for changes

2. **Workload Management:**
   - Calculate faculty workload (credits × subjects)
   - Set maximum workload limits
   - Alert on overload

3. **Conflict Detection:**
   - Check for timetable conflicts
   - Prevent double-booking faculty
   - Suggest alternative faculty

4. **Bulk Operations:**
   - Import faculty assignments from CSV
   - Bulk assign/unassign operations
   - Copy assignments from previous semester

5. **Notifications:**
   - Email faculty when assigned to new subject
   - Notify students of faculty changes
   - Alert admin on unassigned subjects

## Troubleshooting

### Common Issues

**Issue:** Faculty assignment fails with 404 error
- **Solution:** Verify faculty_id exists in database
- **Check:** `FacultyProfile.objects.filter(id=faculty_id).exists()`

**Issue:** Faculty info not showing in API response
- **Solution:** Ensure `select_related('faculty__user')` in queryset
- **Check:** ViewSet queryset includes proper joins

**Issue:** Permission denied when assigning faculty
- **Solution:** Verify user has admin permissions
- **Check:** User `is_staff=True` or has proper role

## Summary

The faculty-subject assignment system is fully functional with:
- ✅ Database model with faculty field
- ✅ Migration applied successfully
- ✅ Seeded test data (4 subjects, 4 faculty)
- ✅ API endpoints for assignment operations
- ✅ Serializer with faculty information
- ✅ Comprehensive test scripts
- ✅ Documentation and usage examples

All components tested and working correctly!
