"""
Swagger/OpenAPI schema definitions for API documentation.

This module contains reusable schema definitions for request/response examples
used across the API documentation.
"""

from drf_yasg import openapi

# ============================================================================
# Authentication Schemas
# ============================================================================

LOGIN_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username', example='student_demo'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password', example='Student@2026'),
    }
)

LOGIN_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['ADMIN', 'FACULTY', 'STUDENT']),
            }
        )
    }
)

REGISTER_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['user', 'profile'],
    properties={
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, example='john_doe'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example='john@example.com'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, example='SecurePass123'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['STUDENT', 'FACULTY', 'ADMIN'], example='STUDENT'),
            }
        ),
        'profile': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reg_no': openapi.Schema(type=openapi.TYPE_STRING, description='Student registration number', example='2026CS001'),
                'enrollment_number': openapi.Schema(type=openapi.TYPE_STRING, example='2026CS001'),
                'employee_id': openapi.Schema(type=openapi.TYPE_STRING, description='Faculty employee ID', example='EMP001'),
                'dob': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='2005-05-15'),
                'gender': openapi.Schema(type=openapi.TYPE_STRING, enum=['M', 'F', 'O'], example='M'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, example='+91-9876543210'),
                'address': openapi.Schema(type=openapi.TYPE_STRING, example='123 Main St'),
                'program_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Program ID (for students)', example=1),
                'department_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'current_semester': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current semester (for students)', example=1),
                'batch_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Batch year (for students)', example=2026),
                'designation': openapi.Schema(type=openapi.TYPE_STRING, description='Designation (for faculty)', example='Professor'),
                'specialization': openapi.Schema(type=openapi.TYPE_STRING, description='Specialization (for faculty)', example='AI/ML'),
                'date_of_joining': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date of joining (for faculty)', example='2020-01-01'),
                'custom_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Institution-specific custom fields (for students)',
                    example={'aadhar_number': '1234-5678-9012', 'samagra_id': 'ABC123456'}
                ),
            }
        )
    }
)

# ============================================================================
# Attendance Schemas
# ============================================================================

BULK_ATTENDANCE_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['subject_id', 'date', 'records'],
    properties={
        'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Subject ID', example=1),
        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Attendance date (YYYY-MM-DD)', example='2026-03-15'),
        'records': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['student_id', 'status'],
                properties={
                    'student_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['Present', 'Absent', 'Late'], example='Present'),
                }
            )
        )
    }
)

BULK_ATTENDANCE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, example='Attendance marked for 3 students.'),
        'subject': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
        'recorded_by': openapi.Schema(type=openapi.TYPE_STRING),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'records': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'student_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'result': openapi.Schema(type=openapi.TYPE_STRING, enum=['created', 'updated']),
                }
            )
        )
    }
)

# ============================================================================
# Semester Registration Schemas
# ============================================================================

SEMESTER_REGISTRATION_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['academic_year', 'semester', 'institute_fee_paid', 'fee_transactions', 'registered_courses'],
    properties={
        'academic_year': openapi.Schema(type=openapi.TYPE_STRING, example='2025-26'),
        'semester': openapi.Schema(type=openapi.TYPE_STRING, example='Jan-Jun 2026'),
        'institute_fee_paid': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
        'hostel_fee_paid': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
        'hostel_room_no': openapi.Schema(type=openapi.TYPE_STRING, example='A-101'),
        'fee_transactions': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description='Up to 3 fee transactions',
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['utr_no', 'bank_name', 'transaction_date', 'amount'],
                properties={
                    'utr_no': openapi.Schema(type=openapi.TYPE_STRING, example='UTR123456789'),
                    'bank_name': openapi.Schema(type=openapi.TYPE_STRING, example='State Bank'),
                    'transaction_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='2026-01-15'),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER, example=50000.00),
                    'account_debited': openapi.Schema(type=openapi.TYPE_STRING, example='XXXX1234'),
                    'account_credited': openapi.Schema(type=openapi.TYPE_STRING, example='INST5678'),
                }
            )
        ),
        'registered_courses': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['subject_id'],
                properties={
                    'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'is_backlog': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                }
            )
        )
    }
)

# ============================================================================
# Grading Schemas
# ============================================================================

FACULTY_GRADE_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['subject_id', 'grades'],
    properties={
        'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        'grades': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['student_id', 'marks_obtained', 'total_marks', 'grade_letter'],
                properties={
                    'student_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                    'marks_obtained': openapi.Schema(type=openapi.TYPE_NUMBER, example=85.5),
                    'total_marks': openapi.Schema(type=openapi.TYPE_NUMBER, example=100),
                    'grade_letter': openapi.Schema(type=openapi.TYPE_STRING, enum=['A', 'A-', 'B', 'B-', 'C', 'C-', 'D', 'F'], example='A'),
                    'remarks': openapi.Schema(type=openapi.TYPE_STRING, example='Excellent performance'),
                }
            )
        )
    }
)

# ============================================================================
# Common Response Schemas
# ============================================================================

ERROR_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error type'),
        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed error message'),
    }
)

SUCCESS_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Response data'),
    }
)

# ============================================================================
# Parameter Definitions
# ============================================================================

SUBJECT_ID_PARAM = openapi.Parameter(
    'subject_id',
    openapi.IN_QUERY,
    description='Subject ID to filter by',
    type=openapi.TYPE_INTEGER,
    required=False
)

BATCH_PARAM = openapi.Parameter(
    'batch',
    openapi.IN_QUERY,
    description='Batch year to filter by (e.g., 2024)',
    type=openapi.TYPE_STRING,
    required=False
)

ACADEMIC_YEAR_PARAM = openapi.Parameter(
    'academic_year',
    openapi.IN_QUERY,
    description='Academic year (e.g., 2025-26)',
    type=openapi.TYPE_STRING,
    required=True
)

SEMESTER_PARAM = openapi.Parameter(
    'semester',
    openapi.IN_QUERY,
    description='Semester period (e.g., Jan-Jun 2026)',
    type=openapi.TYPE_STRING,
    required=True
)

DATE_PARAM = openapi.Parameter(
    'date',
    openapi.IN_QUERY,
    description='Date in YYYY-MM-DD format',
    type=openapi.TYPE_STRING,
    format='date',
    required=True
)

DETAILS_PARAM = openapi.Parameter(
    'details',
    openapi.IN_QUERY,
    description='Include detailed records (true/false)',
    type=openapi.TYPE_BOOLEAN,
    required=False,
    default=False
)
