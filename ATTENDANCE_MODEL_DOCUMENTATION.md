# Attendance Model Documentation

## Overview

Created the Attendance model in the `attendance` app to track daily student attendance in classes with status tracking (PRESENT, ABSENT, LATE).

## Model: Attendance

**Purpose:** Records daily attendance status for students in specific subjects.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `student` | ForeignKey | Link to StudentProfile | CASCADE delete, required |
| `subject` | ForeignKey | Link to Subject | CASCADE delete, required |
| `date` | DateField | Date of the class | Required |
| `status` | CharField | Attendance status | Choices: PRESENT, ABSENT, LATE |
| `remarks` | TextField | Additional notes | Optional |
| `marked_by` | ForeignKey | Faculty who marked attendance | SET_NULL, optional |
| `created_at` | DateTimeField | Record creation timestamp | Auto-set |
| `updated_at` | DateTimeField | Last update timestamp | Auto-update |

### Status Choices

- **PRESENT** - Student attended the class
- **ABSENT** - Student did not attend
- **LATE** - Student arrived late

### Constraints

**Unique Together:** `(student, subject, date)`
- Ensures a student can only have ONE attendance record per subject per day
- Prevents duplicate attendance entries

**Indexes:**
- `(date, subject)` - Fast queries by date and subject
- `(student, date)` - Fast queries by student and date

**Ordering:** Most recent first (`-date`, `student__enrollment_number`)

### Related Names

- `student.attendance_records` - All attendance records for a student
- `subject.attendance_records` - All attendance records for a subject
- `faculty.marked_attendances` - All attendances marked by a faculty member

### String Representation

```python
"2026CS001 - CS101 - 2026-02-11 (PRESENT)"
```

### Properties

#### `is_present`
Returns `True` if status is PRESENT

#### `is_absent`
Returns `True` if status is ABSENT

#### `is_late`
Returns `True` if status is LATE

---

## Use Cases

### 1. Mark Daily Attendance

```python
from attendance.models import Attendance
from users.models import StudentProfile, FacultyProfile
from academics.models import Subject
from datetime import date

# Get student, subject, and faculty
student = StudentProfile.objects.get(enrollment_number='2026CS001')
subject = Subject.objects.get(code='CS101')
faculty = FacultyProfile.objects.get(employee_id='FAC2026001')

# Mark attendance
attendance = Attendance.objects.create(
    student=student,
    subject=subject,
    date=date.today(),
    status='PRESENT',
    marked_by=faculty
)
```

### 2. Bulk Mark Attendance for a Class

```python
from datetime import date

# Get all students enrolled in a subject
students = StudentProfile.objects.filter(
    enrollments__course=subject.course,
    enrollments__status='ENROLLED'
)

# Mark all as present
attendance_records = []
for student in students:
    attendance_records.append(
        Attendance(
            student=student,
            subject=subject,
            date=date.today(),
            status='PRESENT',
            marked_by=faculty
        )
    )

Attendance.objects.bulk_create(attendance_records)
```

### 3. Query Student Attendance

```python
# Get all attendance for a student
student_attendance = student.attendance_records.all()

# Get attendance for specific subject
cs101_attendance = student.attendance_records.filter(subject__code='CS101')

# Get attendance for date range
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=30)
recent_attendance = student.attendance_records.filter(
    date__gte=start_date
)

# Count attendance by status
present_count = student.attendance_records.filter(status='PRESENT').count()
absent_count = student.attendance_records.filter(status='ABSENT').count()
late_count = student.attendance_records.filter(status='LATE').count()
```

### 4. Calculate Attendance Percentage

```python
def calculate_attendance_percentage(student, subject):
    """Calculate attendance percentage for a student in a subject."""
    total = student.attendance_records.filter(subject=subject).count()
    
    if total == 0:
        return 0.0
    
    # Count present and late as attended
    attended = student.attendance_records.filter(
        subject=subject,
        status__in=['PRESENT', 'LATE']
    ).count()
    
    return (attended / total) * 100

# Usage
percentage = calculate_attendance_percentage(student, subject)
print(f"Attendance: {percentage:.2f}%")
```

### 5. Get Subject Attendance Report

```python
from datetime import date

# Get today's attendance for a subject
todays_attendance = Attendance.objects.filter(
    subject=subject,
    date=date.today()
)

# Count by status
present = todays_attendance.filter(status='PRESENT').count()
absent = todays_attendance.filter(status='ABSENT').count()
late = todays_attendance.filter(status='LATE').count()

print(f"Present: {present}, Absent: {absent}, Late: {late}")
```

### 6. Update Attendance Status

```python
# Get attendance record
attendance = Attendance.objects.get(
    student=student,
    subject=subject,
    date=date.today()
)

# Update status
attendance.status = 'LATE'
attendance.remarks = 'Arrived 15 minutes late'
attendance.save()
```

### 7. Check if Attendance Already Marked

```python
from datetime import date

# Check if attendance exists
exists = Attendance.objects.filter(
    student=student,
    subject=subject,
    date=date.today()
).exists()

if exists:
    print("Attendance already marked for today")
else:
    # Mark attendance
    Attendance.objects.create(
        student=student,
        subject=subject,
        date=date.today(),
        status='PRESENT'
    )
```

---

## Admin Configuration

### Features

- **List Display:** Student name, enrollment number, subject, date, status, marked by
- **Filters:** Status, date, department, subject
- **Search:** Student details, subject details, remarks
- **Date Hierarchy:** Easy navigation by date
- **Raw ID Fields:** Student, subject, marked_by (for performance)
- **Bulk Actions:** Mark selected as PRESENT/ABSENT/LATE
- **Custom Methods:** Display related data from foreign keys

### Bulk Actions

Admins can select multiple attendance records and:
1. Mark all as PRESENT
2. Mark all as ABSENT
3. Mark all as LATE

### Admin Interface

Access at: `http://127.0.0.1:8000/admin/attendance/attendance/`

---

## Database Schema

### Table: `attendance_attendance`

```sql
CREATE TABLE attendance_attendance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    remarks TEXT NULL,
    marked_by_id BIGINT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_studentprofile(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES academics_subject(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by_id) REFERENCES users_facultyprofile(id) ON DELETE SET NULL,
    UNIQUE KEY (student_id, subject_id, date),
    INDEX idx_date_subject (date, subject_id),
    INDEX idx_student_date (student_id, date)
);
```

---

## Example Scenarios

### Scenario 1: Daily Class Attendance

```python
from datetime import date
from attendance.models import Attendance

# Faculty marks attendance for today's CS101 class
class_date = date.today()
subject = Subject.objects.get(code='CS101')
faculty = FacultyProfile.objects.get(employee_id='FAC2026001')

# Get enrolled students
enrolled_students = StudentProfile.objects.filter(
    enrollments__course=subject.course,
    enrollments__status='ENROLLED'
)

# Mark attendance
for student in enrolled_students:
    Attendance.objects.create(
        student=student,
        subject=subject,
        date=class_date,
        status='PRESENT',  # Default, can be updated later
        marked_by=faculty
    )
```

### Scenario 2: Attendance Report for Student

```python
def generate_student_attendance_report(student, semester=None):
    """Generate attendance report for a student."""
    
    # Get all attendance records
    records = student.attendance_records.all()
    
    if semester:
        # Filter by semester subjects
        records = records.filter(subject__semester=semester)
    
    # Group by subject
    report = {}
    for subject in Subject.objects.filter(
        attendance_records__student=student
    ).distinct():
        subject_records = records.filter(subject=subject)
        total = subject_records.count()
        present = subject_records.filter(status='PRESENT').count()
        late = subject_records.filter(status='LATE').count()
        absent = subject_records.filter(status='ABSENT').count()
        
        percentage = ((present + late) / total * 100) if total > 0 else 0
        
        report[subject.code] = {
            'subject_name': subject.name,
            'total_classes': total,
            'present': present,
            'late': late,
            'absent': absent,
            'percentage': round(percentage, 2)
        }
    
    return report

# Usage
report = generate_student_attendance_report(student, semester=1)
for code, data in report.items():
    print(f"{code}: {data['percentage']}% ({data['present']}/{data['total_classes']})")
```

### Scenario 3: Low Attendance Alert

```python
def get_students_with_low_attendance(subject, threshold=75):
    """Get students with attendance below threshold."""
    
    from django.db.models import Count, Q
    
    # Get all students with attendance records for this subject
    students = StudentProfile.objects.filter(
        attendance_records__subject=subject
    ).annotate(
        total_classes=Count('attendance_records'),
        attended_classes=Count(
            'attendance_records',
            filter=Q(attendance_records__status__in=['PRESENT', 'LATE'])
        )
    ).distinct()
    
    # Filter by threshold
    low_attendance_students = []
    for student in students:
        if student.total_classes > 0:
            percentage = (student.attended_classes / student.total_classes) * 100
            if percentage < threshold:
                low_attendance_students.append({
                    'student': student,
                    'percentage': round(percentage, 2),
                    'attended': student.attended_classes,
                    'total': student.total_classes
                })
    
    return low_attendance_students

# Usage
low_attendance = get_students_with_low_attendance(subject, threshold=75)
for item in low_attendance:
    print(f"{item['student'].enrollment_number}: {item['percentage']}%")
```

### Scenario 4: Monthly Attendance Summary

```python
from datetime import datetime, timedelta
from django.db.models import Count, Q

def monthly_attendance_summary(subject, year, month):
    """Generate monthly attendance summary for a subject."""
    
    # Get attendance for the month
    records = Attendance.objects.filter(
        subject=subject,
        date__year=year,
        date__month=month
    )
    
    # Count by status
    summary = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT')),
        absent=Count('id', filter=Q(status='ABSENT')),
        late=Count('id', filter=Q(status='LATE'))
    )
    
    # Calculate percentages
    if summary['total'] > 0:
        summary['present_pct'] = round((summary['present'] / summary['total']) * 100, 2)
        summary['absent_pct'] = round((summary['absent'] / summary['total']) * 100, 2)
        summary['late_pct'] = round((summary['late'] / summary['total']) * 100, 2)
    
    return summary

# Usage
summary = monthly_attendance_summary(subject, 2026, 2)
print(f"Total: {summary['total']}")
print(f"Present: {summary['present']} ({summary.get('present_pct', 0)}%)")
print(f"Absent: {summary['absent']} ({summary.get('absent_pct', 0)}%)")
```

---

## Integration with Other Models

### With StudentProfile (users app)
- Students have multiple attendance records
- Access via `student.attendance_records.all()`

### With Subject (academics app)
- Subjects have multiple attendance records
- Access via `subject.attendance_records.all()`

### With FacultyProfile (users app)
- Faculty can mark attendance
- Track who marked each attendance
- Access via `faculty.marked_attendances.all()`

---

## API Integration (Future)

Potential API endpoints:

**Faculty Endpoints:**
- `POST /api/attendance/mark/` - Mark attendance for students
- `GET /api/attendance/class/{subject_id}/{date}/` - Get class attendance
- `PATCH /api/attendance/{id}/` - Update attendance status

**Student Endpoints:**
- `GET /api/attendance/my-attendance/` - Get own attendance records
- `GET /api/attendance/percentage/` - Get attendance percentages

**Admin Endpoints:**
- `GET /api/attendance/reports/low-attendance/` - Low attendance report
- `GET /api/attendance/reports/subject/{subject_id}/` - Subject attendance report
- `GET /api/attendance/reports/student/{student_id}/` - Student attendance report

---

## Validation Rules

1. **Unique Constraint:** One attendance record per student per subject per day
2. **Status Choices:** Must be PRESENT, ABSENT, or LATE
3. **Date:** Cannot be in the future (can be added in clean method)
4. **Student-Subject:** Student should be enrolled in the subject (can be validated)

---

## Migrations

**Created:**
- `attendance/migrations/0001_initial.py` - Creates Attendance table with indexes

**Applied:** ✅ Successfully migrated to database

---

## Files Created/Modified

- ✅ `attendance/models.py` - Created Attendance model
- ✅ `attendance/admin.py` - Registered model with comprehensive admin config
- ✅ `attendance/migrations/0001_initial.py` - Database migration
- ✅ Database table created: `attendance_attendance`

---

## Testing Recommendations

Create tests for:
1. Attendance creation with all fields
2. Unique constraint validation (duplicate attendance for same day)
3. Status choices validation
4. Attendance percentage calculation
5. Bulk attendance marking
6. Query by date range
7. Query by student and subject
8. Update attendance status
9. Property methods (is_present, is_absent, is_late)
10. Low attendance detection

---

## Next Steps

1. Create serializers for Attendance
2. Create API endpoints for marking attendance
3. Add attendance percentage calculation utilities
4. Create attendance reports and analytics
5. Add validation for future dates
6. Add validation for student enrollment in subject
7. Create bulk attendance marking interface
8. Add attendance notifications for low attendance
9. Create attendance export functionality (CSV, PDF)

---

## Benefits

1. **One Record Per Day:** Unique constraint prevents duplicate entries
2. **Flexible Status:** Support for PRESENT, ABSENT, and LATE
3. **Audit Trail:** Track who marked attendance and when
4. **Fast Queries:** Indexes on date and student for performance
5. **Easy Reporting:** Simple queries for attendance percentages
6. **Bulk Operations:** Admin actions for bulk status updates
7. **Historical Data:** Complete attendance history preserved
8. **Integration Ready:** Related names for easy cross-model queries
