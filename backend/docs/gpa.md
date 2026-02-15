# GPA Calculation System Documentation

## Overview

The GPA calculation system provides comprehensive grade point average calculations for students based on their assessment grades and subject credits. The system uses a 10.0 scale and implements weighted averaging based on subject credit hours.

## Features

### 1. GPA Calculation (`calculate_gpa`)

Calculates a student's overall GPA on a 10.0 scale.

**Formula:**
```
GPA = Σ(Subject Grade Point × Subject Credits) / Σ(Subject Credits)
```

**Key Points:**
- Percentage scores are converted to 10-point scale (divide by 10)
- Multiple assessments in the same subject are averaged
- Each subject's average is weighted by its credit hours
- Returns detailed breakdown by subject

**Example:**
```python
from exams.utils import calculate_gpa

result = calculate_gpa(student_id=1)
# Returns:
# {
#     'gpa': Decimal('8.57'),
#     'total_credits': 7,
#     'grades_count': 2,
#     'subject_grades': [
#         {
#             'subject_code': 'CS201',
#             'subject_name': 'Data Structures',
#             'credits': 4,
#             'average_percentage': 90.0,
#             'grade_point': 9.0,
#             'weighted_points': 36.0,
#             'assessments_count': 1
#         },
#         ...
#     ]
# }
```

### 2. Subject Average Calculation (`calculate_subject_average`)

Calculates the average grade for a specific subject.

**Features:**
- Averages all assessments for the subject
- Provides percentage, grade point, and letter grade
- Lists all individual assessment details

**Example:**
```python
from exams.utils import calculate_subject_average

result = calculate_subject_average(student_id=1, subject_id=5)
# Returns:
# {
#     'average_percentage': Decimal('85.00'),
#     'average_grade_point': Decimal('8.50'),
#     'letter_grade': 'B',
#     'assessments_count': 2,
#     'grades': [...]
# }
```

### 3. Student Transcript Generation (`get_student_transcript`)

Generates a complete academic transcript with all grades and GPA.

**Includes:**
- Student information (enrollment number, name, department, etc.)
- Overall GPA and total credits
- Detailed subject-wise breakdown
- Individual assessment details per subject

**Example:**
```python
from exams.utils import get_student_transcript

transcript = get_student_transcript(student_id=1)
# Returns complete transcript with:
# - Student details
# - Overall GPA
# - Subject-wise grades with letter grades
# - All assessment details
```

### 4. Utility Functions

#### Letter Grade Conversion
```python
from exams.utils import get_letter_grade_from_percentage

grade = get_letter_grade_from_percentage(85)  # Returns 'B'
```

**Grading Scale:**
- A: 90-100%
- B: 80-89%
- C: 70-79%
- D: 60-69%
- F: Below 60%

#### Grade Point Conversion
```python
from exams.utils import get_grade_point_from_percentage

gp = get_grade_point_from_percentage(85)  # Returns Decimal('8.5')
```

## Implementation Details

### GPA Calculation Logic

1. **Fetch Grades**: Retrieve all grades for the student
2. **Group by Subject**: Organize grades by subject code
3. **Calculate Subject Averages**: Average all assessments per subject
4. **Convert to Grade Points**: Divide percentage by 10 to get 10-point scale
5. **Apply Credit Weighting**: Multiply grade point by subject credits
6. **Calculate Final GPA**: Sum weighted points / Sum of credits

### Handling Multiple Assessments

When a student has multiple assessments (exams, quizzes, assignments) for the same subject:
- All assessment percentages are averaged
- The average percentage is then converted to a grade point
- This ensures fair representation regardless of assessment count

### Credit Weighting

Subjects with higher credit hours have proportionally more impact on GPA:
```
Subject A: 90% with 4 credits → 9.0 × 4 = 36 weighted points
Subject B: 80% with 3 credits → 8.0 × 3 = 24 weighted points
GPA = (36 + 24) / (4 + 3) = 60 / 7 = 8.57
```

## Database Schema

### Related Models

**Grade Model:**
- `student`: ForeignKey to StudentProfile
- `assessment`: ForeignKey to Assessment
- `marks_obtained`: Decimal field
- Properties: `percentage`, `weighted_marks`

**Assessment Model:**
- `subject`: ForeignKey to Subject
- `max_marks`: Maximum marks for assessment
- `weightage`: Percentage weightage in final grade

**Subject Model:**
- `credits`: Integer field (credit hours)
- `course`: ForeignKey to Course

## Testing

The GPA calculation system includes comprehensive tests:

### Test Coverage (14 tests)

1. **Single Subject GPA**: Verify GPA with one subject
2. **Multiple Subjects**: Test weighted averaging across subjects
3. **Multiple Assessments**: Handle multiple assessments per subject
4. **No Grades**: Return 0.0 GPA when no grades exist
5. **Perfect Score**: Verify 10.0 GPA for 100% scores
6. **Failing Grades**: Handle low scores correctly
7. **Credit Weighting**: Verify proper credit-based weighting
8. **Invalid Student**: Handle non-existent student IDs
9. **Letter Grade Conversion**: Test all grade boundaries
10. **Grade Point Conversion**: Verify percentage to point conversion
11. **Subject Average**: Test subject-specific calculations
12. **Subject Average (No Grades)**: Handle subjects with no grades
13. **Transcript Generation**: Verify complete transcript structure
14. **Subject Sorting**: Ensure subjects are sorted by code

### Running Tests

```bash
# Run all GPA calculation tests
python manage.py test exams.tests.test_gpa_calculation

# Run all exams tests
python manage.py test exams.tests.test_grade_validation exams.tests.test_gpa_calculation
```

## API Integration (Future)

The GPA calculation functions are designed to be easily integrated into REST API endpoints:

```python
# Example API view (to be implemented)
class StudentGPAView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        student = request.user.student_profile
        gpa_data = calculate_gpa(student.id)
        return Response(gpa_data)
```

## Error Handling

The system handles various edge cases:

- **No Grades**: Returns GPA of 0.0 with empty subject list
- **Invalid Student**: Raises `StudentProfile.DoesNotExist`
- **Zero Credits**: Returns GPA of 0.0 (prevents division by zero)
- **Decimal Precision**: All calculations use Decimal for accuracy

## Performance Considerations

- Uses `select_related()` to minimize database queries
- Groups grades in memory to avoid multiple database hits
- Efficient calculation with single pass through grades
- Results can be cached for frequently accessed GPAs

## Future Enhancements

Potential improvements:
1. Semester-wise GPA calculation
2. Cumulative GPA tracking over time
3. GPA trend analysis
4. Comparison with class/department averages
5. Honors/distinction classification based on GPA
6. GPA recalculation on grade updates (signals)
7. Export transcript to PDF format

## Related Documentation

- [Exams Models Documentation](exams/models.py)
- [Grade Validation Tests](exams/tests/test_grade_validation.py)
- [GPA Calculation Tests](exams/tests/test_gpa_calculation.py)
- [Attendance Calculations](ATTENDANCE_CALCULATIONS_DOCUMENTATION.md)
