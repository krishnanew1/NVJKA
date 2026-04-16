# Semester Registration Backend Implementation

## Overview
Implemented a complete backend architecture for Student Semester Subject and Fee Registration system with three new models and a nested API endpoint.

## Models Created

### 1. SemesterRegistration
Located in: `backend/apps/students/models.py`

**Purpose**: Captures a student's semester registration with fee payment status and hostel details.

**Fields**:
- `student` (ForeignKey to StudentProfile)
- `academic_year` (CharField) - e.g., '2025-26'
- `semester` (CharField) - e.g., 'Jan-Jun 2026'
- `institute_fee_paid` (BooleanField)
- `hostel_fee_paid` (BooleanField)
- `hostel_room_no` (CharField, optional)
- `total_credits` (PositiveIntegerField)
- `created_at`, `updated_at` (DateTimeField)

**Constraints**:
- Unique together: (student, academic_year, semester)
- Prevents duplicate registrations for the same semester

### 2. FeeTransaction
Located in: `backend/apps/students/models.py`

**Purpose**: Stores fee payment transaction details. Each semester registration can have up to 3 transactions.

**Fields**:
- `semester_registration` (ForeignKey to SemesterRegistration)
- `utr_no` (CharField) - Unique Transaction Reference number
- `bank_name` (CharField)
- `transaction_date` (DateField)
- `amount` (DecimalField)
- `account_debited` (CharField)
- `account_credited` (CharField)
- `created_at`, `updated_at` (DateTimeField)

**Validation**:
- Maximum 3 fee transactions per semester registration (enforced in model's `clean()` method)

### 3. RegisteredCourse
Located in: `backend/apps/students/models.py`

**Purpose**: Links a semester registration to specific subjects with backlog tracking.

**Fields**:
- `semester_registration` (ForeignKey to SemesterRegistration)
- `subject` (ForeignKey to Subject)
- `is_backlog` (BooleanField, default=False)
- `created_at`, `updated_at` (DateTimeField)

**Constraints**:
- Unique together: (semester_registration, subject)
- Prevents duplicate subject registrations in the same semester

## API Implementation

### Serializers
Located in: `backend/apps/students/serializers.py`

#### FeeTransactionSerializer
- Handles fee transaction data
- Date format: YYYY-MM-DD
- Read-only `id` field

#### RegisteredCourseSerializer
- Nested serializer for course registration
- Write: accepts `subject_id` (PrimaryKeyRelatedField)
- Read: returns full subject details (id, name, code, credits, semester)

#### SemesterRegistrationSerializer
- Main nested serializer accepting:
  - Semester registration details
  - List of `fee_transactions` (up to 3)
  - List of `registered_courses`
- Validates maximum 3 fee transactions
- Includes `student_name` as read-only field
- Handles create and update operations with nested objects

### ViewSet
Located in: `backend/apps/students/views.py`

#### SemesterRegistrationViewSet
**Endpoint**: `/api/students/semester-register/`

**Permissions**:
- Students: Can only view and create their own registrations
- Admin/Faculty: Can view all registrations
- Admin only: Can update/delete registrations

**Methods**:
- `GET /api/students/semester-register/` - List registrations (filtered by role)
- `POST /api/students/semester-register/` - Create new registration (students only)
- `GET /api/students/semester-register/{id}/` - Retrieve specific registration
- `PUT/PATCH /api/students/semester-register/{id}/` - Update registration (admin only)
- `DELETE /api/students/semester-register/{id}/` - Delete registration (admin only)

**Features**:
- Automatically sets student field to logged-in user's profile
- Prevents non-students from creating registrations
- Optimized queries with `select_related` and `prefetch_related`

### URL Configuration
Located in: `backend/apps/students/urls.py`

Added router registration:
```python
router.register(r'semester-register', SemesterRegistrationViewSet, basename='semester-register')
```

## Database Migrations

Migration file: `backend/apps/students/migrations/0004_semesterregistration_feetransaction_registeredcourse.py`

**Applied successfully** - Creates three new tables:
- `students_semesterregistration`
- `students_feetransaction`
- `students_registeredcourse`

## API Usage Examples

### Create Semester Registration (Student)
```bash
POST /api/students/semester-register/
Authorization: Bearer <student_jwt_token>
Content-Type: application/json

{
  "academic_year": "2025-26",
  "semester": "Jan-Jun 2026",
  "institute_fee_paid": true,
  "hostel_fee_paid": true,
  "hostel_room_no": "BH-101",
  "total_credits": 8,
  "fee_transactions": [
    {
      "utr_no": "UTR123456",
      "bank_name": "Test Bank",
      "transaction_date": "2025-12-01",
      "amount": "50000.00",
      "account_debited": "Student Account",
      "account_credited": "Institute Account"
    }
  ],
  "registered_courses": [
    {
      "subject_id": 1,
      "is_backlog": false
    },
    {
      "subject_id": 2,
      "is_backlog": false
    }
  ]
}
```

### List Registrations
```bash
GET /api/students/semester-register/
Authorization: Bearer <jwt_token>
```

**Response** (Student sees only their own):
```json
[
  {
    "id": 1,
    "student": 1,
    "student_name": "John Doe",
    "academic_year": "2025-26",
    "semester": "Jan-Jun 2026",
    "institute_fee_paid": true,
    "hostel_fee_paid": true,
    "hostel_room_no": "BH-101",
    "total_credits": 8,
    "fee_transactions": [
      {
        "id": 1,
        "utr_no": "UTR123456",
        "bank_name": "Test Bank",
        "transaction_date": "2025-12-01",
        "amount": "50000.00",
        "account_debited": "Student Account",
        "account_credited": "Institute Account"
      }
    ],
    "registered_courses": [
      {
        "id": 1,
        "subject": {
          "id": 1,
          "name": "Data Structures",
          "code": "CS201",
          "credits": 4,
          "semester": 3
        },
        "is_backlog": false
      }
    ],
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z"
  }
]
```

## Security Features

1. **Role-Based Access Control**:
   - Students can only create and view their own registrations
   - Admin/Faculty can view all registrations
   - Only Admin can update/delete registrations

2. **Automatic Student Assignment**:
   - Student field is automatically set from `request.user`
   - Prevents students from creating registrations for other students

3. **Validation**:
   - Maximum 3 fee transactions per registration
   - Unique semester registration per student
   - Required fields validation

## Testing

Manual test script created: `backend/test_semester_api.py`

**Test Results**: ✓ All models and relationships work correctly
- SemesterRegistration creation
- FeeTransaction creation (with validation)
- RegisteredCourse creation
- Nested relationships retrieval

## Files Modified/Created

### Created:
1. `backend/apps/students/models.py` - Added 3 new models
2. `backend/apps/students/serializers.py` - Added 3 new serializers
3. `backend/apps/students/views.py` - Added SemesterRegistrationViewSet
4. `backend/apps/students/urls.py` - Added router registration
5. `backend/apps/students/migrations/0004_semesterregistration_feetransaction_registeredcourse.py`
6. `backend/apps/students/tests/test_semester_registration.py` - Test suite
7. `backend/test_semester_api.py` - Manual test script
8. `SEMESTER_REGISTRATION_BACKEND.md` - This documentation

## Next Steps

### Frontend Implementation
To build the frontend for this system, you'll need:

1. **Student Semester Registration Form**:
   - Academic year and semester selection
   - Fee payment checkboxes (institute/hostel)
   - Hostel room number input
   - Dynamic fee transaction forms (up to 3)
   - Subject selection with backlog checkbox
   - Total credits calculation

2. **API Integration**:
   - POST to `/api/students/semester-register/`
   - GET to fetch student's registrations
   - Display registration history

3. **Admin View**:
   - View all semester registrations
   - Filter by academic year, semester, program
   - Export functionality

## Summary

The backend architecture for Student Semester Subject and Fee Registration is complete and functional. The system provides:
- Secure, role-based API endpoints
- Nested data structure for efficient single-request registration
- Proper validation and constraints
- Optimized database queries
- Clean separation of concerns

All models, serializers, views, and URLs are properly configured and tested.
