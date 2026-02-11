Create a test file users/tests/test_profiles.py.

Write a test case that:

Creates a new CustomUser with role='STUDENT'.

Asserts that a StudentProfile was automatically created for them (checking the signal).

Asserts that this user can access the StudentDashboardView but gets a 403 Forbidden if they try to access FacultyDashboardView.# Dashboard API Documentation

## Overview

This document describes the Student and Faculty dashboard API endpoints that provide role-based access to user profile information.

## API Endpoints

### 1. Student Dashboard

**Endpoint:** `GET /api/auth/dashboard/student/`

**Description:** Retrieves the authenticated student's profile information with nested user and department data.

**Authentication:** Required (JWT Token)

**Permissions:** User must be authenticated AND have role='STUDENT'

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "STUDENT",
    "phone_number": "1234567890"
  },
  "enrollment_number": "2026CS001",
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS",
    "description": "Department of Computer Science"
  },
  "current_semester": 3,
  "batch_year": 2026,
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:00:00Z"
}
```

**Error Responses:**

- **401 Unauthorized:** User is not authenticated
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** User is not a student
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Student profile doesn't exist
```json
{
  "error": "Student profile not found",
  "detail": "No student profile exists for this user. Please contact administration."
}
```

---

### 2. Update Student Profile

**Endpoint:** `PATCH /api/auth/dashboard/student/`

**Description:** Partially updates the authenticated student's profile information.

**Authentication:** Required (JWT Token)

**Permissions:** User must be authenticated AND have role='STUDENT'

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (all fields optional):**
```json
{
  "enrollment_number": "2026CS002",
  "department_id": 2,
  "current_semester": 4,
  "batch_year": 2026
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "STUDENT",
    "phone_number": "1234567890"
  },
  "enrollment_number": "2026CS002",
  "department": {
    "id": 2,
    "name": "Electrical Engineering",
    "code": "EE",
    "description": "Department of Electrical Engineering"
  },
  "current_semester": 4,
  "batch_year": 2026,
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:30:00Z"
}
```

**Error Responses:**

- **400 Bad Request:** Validation error
```json
{
  "enrollment_number": ["This enrollment number is already in use."],
  "current_semester": ["Semester must be at least 1."]
}
```

---

### 3. Faculty Dashboard

**Endpoint:** `GET /api/auth/dashboard/faculty/`

**Description:** Retrieves the authenticated faculty member's profile information with nested user and department data.

**Authentication:** Required (JWT Token)

**Permissions:** User must be authenticated AND have role='FACULTY'

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 10,
    "username": "prof_smith",
    "email": "smith@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "role": "FACULTY",
    "phone_number": "9876543210"
  },
  "employee_id": "FAC2026001",
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS",
    "description": "Department of Computer Science"
  },
  "designation": "Professor",
  "specialization": "Machine Learning",
  "date_of_joining": "2020-08-15",
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:00:00Z"
}
```

**Error Responses:**

- **401 Unauthorized:** User is not authenticated
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden:** User is not faculty
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **404 Not Found:** Faculty profile doesn't exist
```json
{
  "error": "Faculty profile not found",
  "detail": "No faculty profile exists for this user. Please contact administration."
}
```

---

### 4. Update Faculty Profile

**Endpoint:** `PATCH /api/auth/dashboard/faculty/`

**Description:** Partially updates the authenticated faculty member's profile information.

**Authentication:** Required (JWT Token)

**Permissions:** User must be authenticated AND have role='FACULTY'

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (all fields optional):**
```json
{
  "employee_id": "FAC2026002",
  "department_id": 2,
  "designation": "Associate Professor",
  "specialization": "Deep Learning",
  "date_of_joining": "2021-01-10"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 10,
    "username": "prof_smith",
    "email": "smith@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "role": "FACULTY",
    "phone_number": "9876543210"
  },
  "employee_id": "FAC2026002",
  "department": {
    "id": 2,
    "name": "Electrical Engineering",
    "code": "EE",
    "description": "Department of Electrical Engineering"
  },
  "designation": "Associate Professor",
  "specialization": "Deep Learning",
  "date_of_joining": "2021-01-10",
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:45:00Z"
}
```

**Error Responses:**

- **400 Bad Request:** Validation error
```json
{
  "employee_id": ["This employee ID is already in use."]
}
```

---

## Authentication Flow

### Step 1: Login and Get Token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 2: Access Dashboard with Token

```bash
curl -X GET http://127.0.0.1:8000/api/auth/dashboard/student/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Custom Permissions

### IsStudent Permission
- Extends `IsAuthenticated`
- Checks if `request.user.role == 'STUDENT'`
- Returns 403 if user is not a student

### IsFaculty Permission
- Extends `IsAuthenticated`
- Checks if `request.user.role == 'FACULTY'`
- Returns 403 if user is not faculty

---

## Serializers

### StudentProfileSerializer
**Fields:**
- `id` (read-only)
- `user` (nested UserBasicSerializer, read-only)
- `enrollment_number` (required, unique)
- `department` (nested DepartmentBasicSerializer, read-only)
- `department_id` (write-only, for updates)
- `current_semester` (required, min: 1)
- `batch_year` (required)
- `created_at` (read-only)
- `updated_at` (read-only)

**Validations:**
- Enrollment number must be unique
- Current semester must be >= 1

### FacultyProfileSerializer
**Fields:**
- `id` (read-only)
- `user` (nested UserBasicSerializer, read-only)
- `employee_id` (required, unique)
- `department` (nested DepartmentBasicSerializer, read-only)
- `department_id` (write-only, required for creation)
- `designation` (required)
- `specialization` (optional)
- `date_of_joining` (optional)
- `created_at` (read-only)
- `updated_at` (read-only)

**Validations:**
- Employee ID must be unique
- Department is required

---

## Testing with cURL

### Test Student Dashboard
```bash
# Login as student
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student_user", "password": "password123"}' \
  | jq -r '.access')

# Get student dashboard
curl -X GET http://127.0.0.1:8000/api/auth/dashboard/student/ \
  -H "Authorization: Bearer $TOKEN"

# Update student profile
curl -X PATCH http://127.0.0.1:8000/api/auth/dashboard/student/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_semester": 4}'
```

### Test Faculty Dashboard
```bash
# Login as faculty
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "faculty_user", "password": "password123"}' \
  | jq -r '.access')

# Get faculty dashboard
curl -X GET http://127.0.0.1:8000/api/auth/dashboard/faculty/ \
  -H "Authorization: Bearer $TOKEN"

# Update faculty profile
curl -X PATCH http://127.0.0.1:8000/api/auth/dashboard/faculty/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"designation": "Associate Professor"}'
```

---

## Files Created/Modified

- ✅ `users/serializers.py` - Created with StudentProfileSerializer and FacultyProfileSerializer
- ✅ `users/views.py` - Created with StudentDashboardView and FacultyDashboardView
- ✅ `users/urls.py` - Updated with dashboard endpoints

## Available Endpoints

- `POST /api/auth/login/` - JWT token authentication
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/dashboard/student/` - Student dashboard (requires STUDENT role)
- `PATCH /api/auth/dashboard/student/` - Update student profile
- `GET /api/auth/dashboard/faculty/` - Faculty dashboard (requires FACULTY role)
- `PATCH /api/auth/dashboard/faculty/` - Update faculty profile
