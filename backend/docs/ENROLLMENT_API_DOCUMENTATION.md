# Enrollment API Documentation

## Overview

The Enrollment API provides endpoints for managing student course enrollments with admin-only access control.

## API Endpoint

### Enroll Student in Course

**Endpoint:** `POST /api/students/enroll/`

**Description:** Enrolls a student in a course. Only admin users can perform this operation.

**Authentication:** Required (JWT Token)

**Permissions:** User must be authenticated AND have role='ADMIN'

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "student_id": 1,
  "course_id": 2
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_id | integer | Yes | ID of the StudentProfile to enroll |
| course_id | integer | Yes | ID of the Course to enroll in |

---

## Success Response

**Status Code:** `201 Created`

**Response Body:**
```json
{
  "message": "Student enrolled successfully",
  "enrollment": {
    "id": 1,
    "student": {
      "id": 1,
      "enrollment_number": "2026CS001",
      "name": "John Doe"
    },
    "course": {
      "id": 2,
      "code": "CS101",
      "name": "Introduction to Programming",
      "credits": 4
    },
    "status": "ENROLLED",
    "date_enrolled": "2026-02-11"
  }
}
```

---

## Error Responses

### 1. Unauthorized (401)

**Condition:** User is not authenticated

**Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 2. Forbidden (403)

**Condition:** User is not an admin (student or faculty trying to enroll)

**Response:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 3. Bad Request (400) - Missing student_id

**Condition:** student_id is not provided in request

**Response:**
```json
{
  "error": "Missing required field",
  "detail": "student_id is required"
}
```

---

### 4. Bad Request (400) - Missing course_id

**Condition:** course_id is not provided in request

**Response:**
```json
{
  "error": "Missing required field",
  "detail": "course_id is required"
}
```

---

### 5. Bad Request (400) - Already Enrolled

**Condition:** Student is already enrolled in the course

**Response:**
```json
{
  "error": "Already enrolled",
  "detail": "Student 2026CS001 is already enrolled in CS101",
  "enrollment": {
    "id": 1,
    "status": "ENROLLED",
    "date_enrolled": "2026-02-10"
  }
}
```

---

### 6. Not Found (404) - Student Not Found

**Condition:** student_id does not exist

**Response:**
```json
{
  "error": "Student not found",
  "detail": "No student profile found with id 999"
}
```

---

### 7. Not Found (404) - Course Not Found

**Condition:** course_id does not exist

**Response:**
```json
{
  "error": "Course not found",
  "detail": "No course found with id 999"
}
```

---

### 8. Internal Server Error (500)

**Condition:** Database integrity error

**Response:**
```json
{
  "error": "Database error",
  "detail": "Failed to create enrollment due to database constraint"
}
```

---

## Validation Rules

1. **Admin Only:** Only users with role='ADMIN' can enroll students
2. **Unique Enrollment:** A student can only be enrolled in a course once
3. **Valid Student:** student_id must reference an existing StudentProfile
4. **Valid Course:** course_id must reference an existing Course
5. **Required Fields:** Both student_id and course_id are required

---

## Usage Examples

### Example 1: Successful Enrollment

```bash
# Step 1: Login as admin
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin_password"
  }'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Step 2: Enroll student
curl -X POST http://127.0.0.1:8000/api/students/enroll/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 2
  }'

# Response:
{
  "message": "Student enrolled successfully",
  "enrollment": {
    "id": 1,
    "student": {
      "id": 1,
      "enrollment_number": "2026CS001",
      "name": "John Doe"
    },
    "course": {
      "id": 2,
      "code": "CS101",
      "name": "Introduction to Programming",
      "credits": 4
    },
    "status": "ENROLLED",
    "date_enrolled": "2026-02-11"
  }
}
```

---

### Example 2: Non-Admin Attempt (Forbidden)

```bash
# Login as student
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student",
    "password": "student_password"
  }'

# Try to enroll (will fail)
curl -X POST http://127.0.0.1:8000/api/students/enroll/ \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 2
  }'

# Response: 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Example 3: Duplicate Enrollment Attempt

```bash
# First enrollment (succeeds)
curl -X POST http://127.0.0.1:8000/api/students/enroll/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 2
  }'

# Second enrollment attempt (fails)
curl -X POST http://127.0.0.1:8000/api/students/enroll/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 2
  }'

# Response: 400 Bad Request
{
  "error": "Already enrolled",
  "detail": "Student 2026CS001 is already enrolled in CS101",
  "enrollment": {
    "id": 1,
    "status": "ENROLLED",
    "date_enrolled": "2026-02-11"
  }
}
```

---

## Implementation Details

### Custom Permission Class

**IsAdmin Permission:**
- Extends `IsAuthenticated`
- Checks if `request.user.role == 'ADMIN'`
- Returns 403 if user is not an admin

### Enrollment Logic

1. **Validate Request:** Check for required fields (student_id, course_id)
2. **Fetch Student:** Get StudentProfile by ID or return 404
3. **Fetch Course:** Get Course by ID or return 404
4. **Check Existing:** Query for existing enrollment
5. **Create Enrollment:** If not exists, create with status='ENROLLED'
6. **Return Response:** Return enrollment details with nested data

### Database Constraints

- **Unique Together:** (student, course) prevents duplicate enrollments
- **Foreign Keys:** CASCADE delete on student and course
- **Status Choices:** ENROLLED, COMPLETED, DROPPED, WITHDRAWN

---

## Testing

### Test Coverage: 9/9 Tests Passing ✅

**Test Cases:**
1. ✅ Admin can enroll student successfully
2. ✅ Cannot enroll student twice in same course
3. ✅ Non-admin users cannot enroll students (403)
4. ✅ Unauthenticated users cannot enroll students (401)
5. ✅ Missing student_id returns validation error (400)
6. ✅ Missing course_id returns validation error (400)
7. ✅ Invalid student_id returns 404
8. ✅ Invalid course_id returns 404
9. ✅ Admin can enroll student in multiple courses

**Test File:** `students/tests/test_enrollment.py`

**Run Tests:**
```bash
python manage.py test students.tests.test_enrollment
```

---

## Files Created/Modified

- ✅ `students/views.py` - Created EnrollStudentView with IsAdmin permission
- ✅ `students/urls.py` - Created URL configuration
- ✅ `academic_erp_project/urls.py` - Included students URLs
- ✅ `students/tests/test_enrollment.py` - Comprehensive test suite
- ✅ `students/tests/__init__.py` - Test package initialization

---

## Available Endpoints Summary

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/students/enroll/` | IsAdmin | Enroll student in course |

---

## Next Steps

Potential enhancements:
1. Add endpoint to list student's enrollments
2. Add endpoint to update enrollment status
3. Add endpoint to drop/withdraw from course
4. Add prerequisite validation
5. Add course capacity checking
6. Add enrollment period validation
7. Add bulk enrollment endpoint
8. Add enrollment statistics endpoint

---

## Security Considerations

1. **Admin-Only Access:** Only admins can enroll students
2. **Authentication Required:** All requests must be authenticated
3. **Input Validation:** All inputs are validated before processing
4. **Database Constraints:** Unique constraints prevent duplicate enrollments
5. **Error Handling:** Proper error messages without exposing sensitive data
