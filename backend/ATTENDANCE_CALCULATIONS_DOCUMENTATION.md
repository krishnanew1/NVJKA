# Attendance Calculations Documentation

## Overview

Created utility functions for calculating attendance percentages and generating attendance summaries, along with comprehensive tests to verify accuracy.

## Files Created

### 1. `attendance/utils.py`

Utility module containing attendance calculation functions.

#### Functions

##### `calculate_attendance_percentage(student, subject=None)`

Calculates attendance percentage for a student.

**Parameters:**
- `student` (StudentProfile): The student whose attendance to calculate
- `subject` (Subject, optional): Specific subject to calculate for. If None, calculates overall attendance.

**Returns:**
- `float`: Attendance percentage (0-100)

**Logic:**
- Counts total attendance records
- Counts records with status PRESENT or LATE as "attended"
- Returns (attended / total) * 100
- Returns 0.0 if no records exist

**Example:**
```python
from attendance.utils import calculate_attendance_percentage

percentage = calculate_attendance_percentage(student, subject)
print(f"Attendance: {percentage:.2f}%")  # Output: Attendance: 80.00%
```

---

##### `get_attendance_summary(student, subject=None)`

Gets detailed attendance summary for a student.

**Parameters:**
- `student` (StudentProfile): The student whose attendance to summarize
- `subject` (Subject, optional): Specific subject to summarize. If None, summarizes overall attendance.

**Returns:**
- `dict`: Summary containing:
  - `total` (int): Total attendance records
  - `present` (int): Number of PRESENT records
  - `absent` (int): Number of ABSENT records
  - `late` (int): Number of LATE records
  - `attended` (int): Number of attended classes (PRESENT + LATE)
  - `percentage` (float): Attendance percentage (rounded to 2 decimals)

**Example:**
```python
from attendance.utils import get_attendance_summary

summary = get_attendance_summary(student, subject)
print(f"Total: {summary['total']}")
print(f"Present: {summary['present']}")
print(f"Absent: {summary['absent']}")
print(f"Late: {summary['late']}")
print(f"Percentage: {summary['percentage']}%")
```

**Output:**
```
Total: 10
Present: 8
Absent: 2
Late: 0
Percentage: 80.0%
```

---

### 2. `attendance/tests/test_calculations.py`

Comprehensive test suite for attendance calculations.

## Test Coverage: 9/9 Tests Passing ✅

### Test Cases

#### 1. ✅ `test_attendance_percentage_with_8_present_2_absent`
**Purpose:** Verify 80% calculation with 8 PRESENT and 2 ABSENT records

**Test Steps:**
1. Create 8 attendance records with status PRESENT
2. Create 2 attendance records with status ABSENT
3. Calculate attendance percentage
4. Assert percentage equals 80.0%
5. Verify total records count (10)
6. Verify present count (8)
7. Verify absent count (2)

**Expected Result:** Percentage = 80.0%

---

#### 2. ✅ `test_attendance_percentage_with_all_present`
**Purpose:** Verify 100% calculation when all records are PRESENT

**Test Steps:**
1. Create 10 attendance records with status PRESENT
2. Calculate attendance percentage
3. Assert percentage equals 100.0%

**Expected Result:** Percentage = 100.0%

---

#### 3. ✅ `test_attendance_percentage_with_all_absent`
**Purpose:** Verify 0% calculation when all records are ABSENT

**Test Steps:**
1. Create 10 attendance records with status ABSENT
2. Calculate attendance percentage
3. Assert percentage equals 0.0%

**Expected Result:** Percentage = 0.0%

---

#### 4. ✅ `test_attendance_percentage_with_no_records`
**Purpose:** Verify 0% calculation when no attendance records exist

**Test Steps:**
1. Don't create any attendance records
2. Calculate attendance percentage
3. Assert percentage equals 0.0%

**Expected Result:** Percentage = 0.0%

---

#### 5. ✅ `test_attendance_percentage_includes_late_as_attended`
**Purpose:** Verify LATE status is counted as attended

**Test Steps:**
1. Create 7 PRESENT records
2. Create 2 LATE records
3. Create 1 ABSENT record
4. Calculate attendance percentage
5. Assert percentage equals 90.0% (7 + 2 = 9 attended out of 10)

**Expected Result:** Percentage = 90.0%

---

#### 6. ✅ `test_attendance_summary_returns_correct_counts`
**Purpose:** Verify get_attendance_summary returns accurate counts

**Test Steps:**
1. Create 8 PRESENT and 2 ABSENT records
2. Get attendance summary
3. Assert all counts are correct:
   - total = 10
   - present = 8
   - absent = 2
   - late = 0
   - attended = 8
   - percentage = 80.0

**Expected Result:** All counts match expected values

---

#### 7. ✅ `test_attendance_summary_with_mixed_statuses`
**Purpose:** Verify summary with PRESENT, ABSENT, and LATE statuses

**Test Steps:**
1. Create 5 PRESENT records
2. Create 3 LATE records
3. Create 2 ABSENT records
4. Get attendance summary
5. Assert counts:
   - total = 10
   - present = 5
   - late = 3
   - absent = 2
   - attended = 8 (5 + 3)
   - percentage = 80.0

**Expected Result:** All counts match expected values

---

#### 8. ✅ `test_attendance_percentage_for_specific_subject`
**Purpose:** Verify percentage calculation for specific subjects

**Test Steps:**
1. Create two subjects
2. Create attendance for subject 1: 8 PRESENT, 2 ABSENT (80%)
3. Create attendance for subject 2: 6 PRESENT, 4 ABSENT (60%)
4. Calculate percentage for each subject separately
5. Assert subject 1 = 80.0%
6. Assert subject 2 = 60.0%

**Expected Result:** Each subject has correct independent percentage

---

#### 9. ✅ `test_overall_attendance_percentage_without_subject`
**Purpose:** Verify overall attendance calculation across all subjects

**Test Steps:**
1. Create two subjects
2. Create attendance for subject 1: 8 PRESENT, 2 ABSENT
3. Create attendance for subject 2: 6 PRESENT, 4 ABSENT
4. Calculate overall percentage (no subject filter)
5. Assert overall = 70.0% (14 PRESENT out of 20 total)

**Expected Result:** Overall percentage = 70.0%

---

## Usage Examples

### Example 1: Calculate Subject Attendance

```python
from attendance.utils import calculate_attendance_percentage
from users.models import StudentProfile
from academics.models import Subject

# Get student and subject
student = StudentProfile.objects.get(enrollment_number='2026CS001')
subject = Subject.objects.get(code='CS101')

# Calculate percentage
percentage = calculate_attendance_percentage(student, subject)

if percentage < 75:
    print(f"Warning: Low attendance ({percentage:.2f}%)")
else:
    print(f"Good attendance: {percentage:.2f}%")
```

---

### Example 2: Generate Attendance Report

```python
from attendance.utils import get_attendance_summary

# Get detailed summary
summary = get_attendance_summary(student, subject)

print(f"Attendance Report for {student.enrollment_number}")
print(f"Subject: {subject.code}")
print(f"=" * 40)
print(f"Total Classes: {summary['total']}")
print(f"Present: {summary['present']}")
print(f"Late: {summary['late']}")
print(f"Absent: {summary['absent']}")
print(f"Attended: {summary['attended']}")
print(f"Percentage: {summary['percentage']}%")
```

**Output:**
```
Attendance Report for 2026CS001
Subject: CS101
========================================
Total Classes: 10
Present: 8
Late: 0
Absent: 2
Attended: 8
Percentage: 80.0%
```

---

### Example 3: Overall Attendance Across All Subjects

```python
# Calculate overall attendance (no subject filter)
overall_percentage = calculate_attendance_percentage(student, subject=None)
overall_summary = get_attendance_summary(student, subject=None)

print(f"Overall Attendance: {overall_percentage:.2f}%")
print(f"Total Classes Attended: {overall_summary['attended']}/{overall_summary['total']}")
```

---

### Example 4: Check Attendance Threshold

```python
def check_attendance_eligibility(student, subject, threshold=75):
    """
    Check if student meets minimum attendance requirement.
    """
    percentage = calculate_attendance_percentage(student, subject)
    
    if percentage >= threshold:
        return {
            'eligible': True,
            'percentage': percentage,
            'message': f'Student meets attendance requirement ({percentage:.2f}%)'
        }
    else:
        shortage = threshold - percentage
        return {
            'eligible': False,
            'percentage': percentage,
            'message': f'Student needs {shortage:.2f}% more attendance'
        }

# Usage
result = check_attendance_eligibility(student, subject, threshold=75)
print(result['message'])
```

---

### Example 5: Generate Report for All Subjects

```python
from academics.models import Subject

def generate_full_attendance_report(student):
    """
    Generate attendance report for all subjects.
    """
    subjects = Subject.objects.filter(
        attendance_records__student=student
    ).distinct()
    
    report = []
    for subject in subjects:
        summary = get_attendance_summary(student, subject)
        report.append({
            'subject_code': subject.code,
            'subject_name': subject.name,
            'percentage': summary['percentage'],
            'attended': summary['attended'],
            'total': summary['total']
        })
    
    return report

# Usage
report = generate_full_attendance_report(student)
for item in report:
    print(f"{item['subject_code']}: {item['percentage']}% ({item['attended']}/{item['total']})")
```

---

## Key Features

✅ **Accurate Calculations** - Verified with comprehensive tests  
✅ **LATE Counted as Attended** - LATE status counts toward attendance  
✅ **Subject-Specific** - Calculate for individual subjects  
✅ **Overall Attendance** - Calculate across all subjects  
✅ **Detailed Summary** - Get counts for all status types  
✅ **Zero-Safe** - Returns 0% when no records exist  
✅ **Rounded Percentages** - Summary returns rounded values  

---

## Test Results

```
Ran 9 tests in 2.001s

OK
```

All tests passed successfully! ✅

---

## Integration with Models

### Attendance Model
- Uses `student.attendance_records` related name
- Filters by `status` field (PRESENT, ABSENT, LATE)
- Filters by `subject` when specified

### StudentProfile Model
- Access via `student.attendance_records.all()`
- Can filter by subject, date, status

### Subject Model
- Can query attendance for specific subject
- Supports multiple students per subject

---

## API Integration (Future)

Potential API endpoints using these utilities:

**Student Endpoints:**
- `GET /api/students/my-attendance/` - Get own attendance summary
- `GET /api/students/my-attendance/{subject_id}/` - Get subject-specific attendance

**Faculty Endpoints:**
- `GET /api/faculty/class-attendance/{subject_id}/` - Get class attendance summary
- `GET /api/faculty/low-attendance/` - Get students with low attendance

**Admin Endpoints:**
- `GET /api/reports/attendance/student/{student_id}/` - Student attendance report
- `GET /api/reports/attendance/subject/{subject_id}/` - Subject attendance report
- `GET /api/reports/attendance/low-attendance/` - System-wide low attendance report

---

## Benefits

1. **Reusable Functions** - Can be used in views, reports, and scripts
2. **Well-Tested** - 9 comprehensive tests ensure accuracy
3. **Flexible** - Works for specific subjects or overall attendance
4. **Efficient** - Uses Django ORM efficiently
5. **Easy to Use** - Simple function calls with clear parameters
6. **Accurate** - Handles edge cases (no records, all absent, etc.)
7. **Documented** - Clear docstrings and examples

---

## Next Steps

1. Create API endpoints using these utilities
2. Add attendance reports in admin panel
3. Create student attendance dashboard
4. Add low attendance alerts/notifications
5. Generate attendance certificates
6. Export attendance reports (CSV, PDF)
7. Add attendance trends and analytics
8. Create attendance prediction models
