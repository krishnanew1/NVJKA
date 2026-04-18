# Requirements Document

## Introduction

The Academic ERP Management System is a comprehensive, multi-role digital platform designed to manage institutional workflows for educational institutions. The system streamlines administrative tasks, faculty classroom management, and student academic lifecycles into a single, centralized portal. It provides role-based access control for Admins, Faculty, and Students, with a headless Django backend, MySQL database, and React frontend using JWT authentication for secure, stateless access.

## Glossary

- **System**: The Academic ERP Management System
- **Admin**: A user with administrative privileges who manages institutional structure, users, and system configuration
- **Faculty**: A user who teaches subjects, marks attendance, and manages grades
- **Student**: A user who enrolls in courses, views grades, and accesses academic records
- **User**: Any authenticated person using the system (Admin, Faculty, or Student)
- **Department**: An academic organizational unit (e.g., Computer Science, Mathematics)
- **Program**: An academic degree program with defined duration and credit requirements (e.g., B.Tech, M.Sc)
- **Course**: A specific instance of a program for a batch year
- **Subject**: An individual academic unit taught within a program
- **Batch**: A group of students who enrolled in the same year
- **Semester**: A time period within an academic year (typically 6 months)
- **Enrollment**: The registration of a student into a specific course
- **Timetable**: A schedule mapping subjects to time slots, classrooms, and faculty
- **Attendance_Record**: A record of student presence or absence for a specific subject session
- **Assessment**: An examination or evaluation component (quiz, midterm, final)
- **Grade**: A numerical or letter score assigned to a student for an assessment
- **Transcript**: A comprehensive academic record showing all grades and GPA/CGPA
- **JWT**: JSON Web Token used for stateless authentication
- **Custom_Registration_Field**: Institution-specific data fields for student registration
- **Audit_Log**: A record of all system operations for security and compliance

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a User, I want to securely authenticate and access role-appropriate features, so that I can perform my institutional responsibilities.

#### Acceptance Criteria

1. WHEN a User submits valid credentials, THE System SHALL generate a JWT access token and refresh token
2. WHEN a User submits invalid credentials, THE System SHALL return an authentication error within 200ms
3. WHEN an access token expires, THE System SHALL accept a valid refresh token to generate a new access token
4. THE System SHALL enforce role-based access control for all API endpoints
5. WHEN an unauthorized User attempts to access a restricted resource, THE System SHALL return a 403 Forbidden response
6. THE System SHALL hash all passwords using Django's PBKDF2 algorithm before storage
7. WHEN a User logs out, THE System SHALL invalidate the refresh token

### Requirement 2: Multi-Role User Management

**User Story:** As an Admin, I want to create and manage user accounts with different roles, so that I can control system access.

#### Acceptance Criteria

1. THE System SHALL support three user roles: Admin, Faculty, and Student
2. WHEN an Admin creates a new user, THE System SHALL require username, email, password, and role
3. THE System SHALL create role-specific profiles (StudentProfile or FacultyProfile) based on the assigned role
4. WHEN an Admin updates a user's role, THE System SHALL update the corresponding profile associations
5. THE System SHALL prevent duplicate usernames and email addresses
6. WHEN an Admin deactivates a user, THE System SHALL prevent that user from authenticating
7. THE System SHALL log all user management operations in the Audit_Log

### Requirement 3: Academic Structure Management

**User Story:** As an Admin, I want to define the institutional academic structure, so that I can organize programs and courses hierarchically.

#### Acceptance Criteria

1. THE System SHALL support a hierarchy: Department → Program → Course → Subject
2. WHEN an Admin creates a Department, THE System SHALL require a unique name and code
3. WHEN an Admin creates a Program, THE System SHALL require name, code, department, duration_years, and total_credits
4. WHEN an Admin creates a Course, THE System SHALL link it to a Program and specify batch_year and total_semesters
5. WHEN an Admin creates a Subject, THE System SHALL require name, code, credits, semester, and department
6. THE System SHALL prevent deletion of a Department that has associated Programs
7. THE System SHALL allow Admins to assign Faculty to Subjects through ClassAssignment records

### Requirement 4: Dynamic Custom Registration Fields

**User Story:** As an Admin, I want to define custom registration fields for students, so that I can collect institution-specific data without code changes.

#### Acceptance Criteria

1. THE System SHALL allow Admins to create Custom_Registration_Fields with field_name, field_label, field_type, and is_required
2. THE System SHALL support field types: text, number, email, date, dropdown, and checkbox
3. WHEN an Admin creates a Custom_Registration_Field, THE System SHALL assign an order value for display sequence
4. THE System SHALL store custom field values in StudentProfile.custom_data as JSON
5. WHEN a Student registers, THE System SHALL validate required custom fields before saving
6. THE System SHALL return active Custom_Registration_Fields via API endpoint for frontend rendering
7. WHEN an Admin deactivates a Custom_Registration_Field, THE System SHALL exclude it from new registrations while preserving existing data

### Requirement 5: Student Enrollment and Registration

**User Story:** As a Student, I want to enroll in a course and register for semesters, so that I can begin my academic journey.

#### Acceptance Criteria

1. WHEN a Student enrolls in a Course, THE System SHALL create an Enrollment record with enrollment_date and current_semester
2. THE System SHALL prevent duplicate enrollments for the same Student and Course
3. WHEN a Student registers for a semester, THE System SHALL create a SemesterRegistration record
4. THE System SHALL allow Students to register for multiple Subjects within a semester through RegisteredCourse records
5. WHEN a Student registers for a Subject, THE System SHALL validate that the Subject belongs to the current semester
6. THE System SHALL calculate and store total_credits for each SemesterRegistration
7. THE System SHALL prevent Students from registering for Subjects exceeding the Program's credit limit per semester

### Requirement 6: Automated Timetable Generation

**User Story:** As an Admin, I want to automatically generate timetables for batches, so that I can schedule classes without conflicts.

#### Acceptance Criteria

1. WHEN an Admin requests timetable generation, THE System SHALL require batch_year, department_id, semester, and academic_year
2. THE System SHALL assign each Subject to available time slots (Monday-Friday, 9:00-17:00)
3. THE System SHALL prevent scheduling conflicts where a Faculty is assigned to multiple Subjects at the same time
4. THE System SHALL prevent scheduling conflicts where a classroom is assigned to multiple Subjects at the same time
5. THE System SHALL assign Subjects to classrooms based on availability
6. WHEN timetable generation fails due to conflicts, THE System SHALL return a descriptive error message
7. THE System SHALL store generated Timetable records with day, time_slot, subject, faculty, and classroom

### Requirement 7: Attendance Tracking and Reporting

**User Story:** As a Faculty, I want to mark and track student attendance, so that I can monitor class participation.

#### Acceptance Criteria

1. WHEN Faculty marks attendance, THE System SHALL create Attendance_Record entries with student_id, subject_id, date, and status
2. THE System SHALL support attendance statuses: Present, Absent, Late, and Excused
3. THE System SHALL support bulk attendance marking for multiple Students in a single API call
4. THE System SHALL prevent duplicate Attendance_Records for the same Student, Subject, and date
5. WHEN Faculty submits an attendance report, THE System SHALL create an AttendanceReportSubmission record
6. THE System SHALL calculate attendance percentage as (Present + Late) / Total_Sessions × 100
7. WHEN a Student requests attendance summary, THE System SHALL return attendance percentage per Subject

### Requirement 8: Assessment and Grading System

**User Story:** As a Faculty, I want to create assessments and assign grades, so that I can evaluate student performance.

#### Acceptance Criteria

1. WHEN Faculty creates an Assessment, THE System SHALL require subject_id, assessment_type, max_marks, and weightage
2. THE System SHALL support assessment types: Quiz, Assignment, Midterm, Final, and Project
3. WHEN Faculty assigns a Grade, THE System SHALL create a StudentGrade record with student_id, assessment_id, and marks_obtained
4. THE System SHALL validate that marks_obtained does not exceed Assessment.max_marks
5. THE System SHALL calculate weighted scores as (marks_obtained / max_marks) × weightage
6. THE System SHALL prevent Faculty from grading Assessments for Subjects they are not assigned to
7. THE System SHALL allow Faculty to update grades before the semester is finalized

### Requirement 9: Automated Transcript Generation

**User Story:** As a Student, I want to view my complete academic transcript, so that I can track my academic progress.

#### Acceptance Criteria

1. WHEN a Student requests a transcript, THE System SHALL return all completed semesters with grades
2. THE System SHALL calculate semester GPA as Σ(grade_points × credits) / Σ(credits) for each semester
3. THE System SHALL calculate cumulative CGPA as Σ(semester_GPA × semester_credits) / Σ(semester_credits)
4. THE System SHALL convert percentage scores to grade points using a 10-point scale
5. THE System SHALL include Subject name, code, credits, grade, and grade_points in the transcript
6. THE System SHALL mark incomplete Assessments as "In Progress" in the transcript
7. THE System SHALL generate transcripts in JSON format via API endpoint

### Requirement 10: Communication and Notice Board

**User Story:** As an Admin or Faculty, I want to post notices and share resources, so that I can communicate with students and faculty.

#### Acceptance Criteria

1. WHEN an Admin or Faculty creates a Notice, THE System SHALL require title, content, and target_audience
2. THE System SHALL support target audiences: All, Students, Faculty, and Department-specific
3. WHEN a Notice is created, THE System SHALL set is_active to true and record created_at timestamp
4. THE System SHALL allow file uploads for Resource sharing with file_type and file_url
5. WHEN a User requests notices, THE System SHALL return only active notices for their role and department
6. THE System SHALL support Notice expiration by allowing Admins to set is_active to false
7. THE System SHALL log all Notice and Resource creation operations in Audit_Log

### Requirement 11: Audit Logging and Security

**User Story:** As an Admin, I want to track all system operations, so that I can ensure security and compliance.

#### Acceptance Criteria

1. THE System SHALL create an Audit_Log entry for every create, update, and delete operation
2. WHEN an operation is logged, THE System SHALL record user, action, model_name, object_id, and timestamp
3. THE System SHALL store changed_data as JSON showing before and after values for updates
4. THE System SHALL prevent non-Admin users from accessing Audit_Log records
5. WHEN an Admin queries Audit_Logs, THE System SHALL support filtering by user, action, model_name, and date range
6. THE System SHALL retain Audit_Log records for a minimum of 1 year
7. THE System SHALL log failed authentication attempts with IP address and timestamp

### Requirement 12: Department-Level Access Control

**User Story:** As a Faculty member, I want to access only my department's data, so that I can maintain data privacy.

#### Acceptance Criteria

1. WHEN a Faculty user is created, THE System SHALL assign them to a specific Department
2. THE System SHALL restrict Faculty access to Subjects, Students, and Courses within their Department
3. WHEN Faculty requests student lists, THE System SHALL return only Students enrolled in their Department's Courses
4. THE System SHALL allow Admins to access data across all Departments
5. WHEN Faculty attempts to access another Department's data, THE System SHALL return a 403 Forbidden response
6. THE System SHALL apply department filtering automatically in all Faculty API endpoints
7. THE System SHALL allow cross-department access only when explicitly granted by Admin

### Requirement 13: Fee Management and Transactions

**User Story:** As an Admin, I want to track student fee payments, so that I can manage institutional finances.

#### Acceptance Criteria

1. WHEN a Student enrolls, THE System SHALL create a FeeTransaction record with amount_due
2. THE System SHALL support transaction types: Tuition, Hostel, Library, and Miscellaneous
3. WHEN a payment is recorded, THE System SHALL update amount_paid and calculate balance as amount_due - amount_paid
4. THE System SHALL support payment statuses: Pending, Partial, Paid, and Overdue
5. WHEN a Student requests fee summary, THE System SHALL return all FeeTransaction records with current balance
6. THE System SHALL prevent Students from registering for new semesters if balance is overdue
7. THE System SHALL log all fee transactions in Audit_Log

### Requirement 14: Academic History Tracking

**User Story:** As a Student, I want to view my complete academic history, so that I can track my progress over time.

#### Acceptance Criteria

1. WHEN a semester is completed, THE System SHALL create an AcademicHistory record with semester, year, and GPA
2. THE System SHALL store subjects_taken as JSON array with subject names and grades
3. THE System SHALL calculate cumulative CGPA and store it in each AcademicHistory record
4. WHEN a Student requests academic history, THE System SHALL return records ordered by year and semester
5. THE System SHALL include total_credits_earned in each AcademicHistory record
6. THE System SHALL prevent modification of AcademicHistory records after semester finalization
7. THE System SHALL allow Admins to correct AcademicHistory records with Audit_Log entry

### Requirement 15: Responsive Frontend Interface

**User Story:** As a User, I want to access the system from any device, so that I can work from anywhere.

#### Acceptance Criteria

1. THE System SHALL provide a React-based frontend that renders correctly on desktop, tablet, and mobile devices
2. THE System SHALL support screen widths from 320px (mobile) to 1920px (desktop)
3. WHEN a User switches between light and dark themes, THE System SHALL persist the preference in browser storage
4. THE System SHALL display role-specific navigation menus based on JWT token claims
5. THE System SHALL show loading indicators during API calls exceeding 500ms
6. WHEN an API error occurs, THE System SHALL display user-friendly error messages via toast notifications
7. THE System SHALL implement secure routing that redirects unauthenticated users to the login page

### Requirement 16: API Documentation and Developer Experience

**User Story:** As a Developer, I want comprehensive API documentation, so that I can integrate with the system easily.

#### Acceptance Criteria

1. THE System SHALL provide Swagger UI documentation at /swagger/ endpoint
2. THE System SHALL provide ReDoc documentation at /redoc/ endpoint
3. THE System SHALL include request/response schemas for all API endpoints in the documentation
4. THE System SHALL document authentication requirements for each endpoint
5. THE System SHALL provide example requests and responses in the documentation
6. THE System SHALL include error code descriptions (400, 401, 403, 404, 500) in the documentation
7. THE System SHALL auto-generate API documentation from Django REST Framework serializers and viewsets

### Requirement 17: Database Performance and Optimization

**User Story:** As a System Administrator, I want optimized database queries, so that the system performs well under load.

#### Acceptance Criteria

1. THE System SHALL use select_related for foreign key relationships to reduce database queries
2. THE System SHALL use prefetch_related for many-to-many and reverse foreign key relationships
3. WHEN querying Student transcripts, THE System SHALL fetch all related data in a maximum of 3 database queries
4. THE System SHALL add database indexes on frequently queried fields (username, email, enrollment_number)
5. THE System SHALL implement database connection pooling for concurrent requests
6. WHEN the system handles 100 concurrent API requests, THE System SHALL maintain response times under 1 second
7. THE System SHALL use database transactions for operations that modify multiple related records

### Requirement 18: CORS and Frontend Integration

**User Story:** As a Frontend Developer, I want secure cross-origin access, so that I can build the React application.

#### Acceptance Criteria

1. THE System SHALL allow CORS requests from configured frontend origins
2. THE System SHALL support CORS origins defined in environment variable CORS_ALLOWED_ORIGINS
3. THE System SHALL include Access-Control-Allow-Credentials header for authenticated requests
4. THE System SHALL allow HTTP methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
5. THE System SHALL allow headers: Content-Type, Authorization, Accept
6. WHEN a preflight OPTIONS request is received, THE System SHALL respond within 100ms
7. THE System SHALL reject CORS requests from non-whitelisted origins with 403 Forbidden

### Requirement 19: Production Deployment Readiness

**User Story:** As a DevOps Engineer, I want production-ready configuration, so that I can deploy the system securely.

#### Acceptance Criteria

1. WHEN DEBUG is False, THE System SHALL disable detailed error messages in API responses
2. THE System SHALL require ALLOWED_HOSTS configuration in production mode
3. THE System SHALL enforce HTTPS in production by setting SECURE_SSL_REDIRECT to True
4. THE System SHALL set secure cookie flags (SECURE, HttpOnly, SameSite) for session and CSRF tokens
5. THE System SHALL support environment-based configuration via .env file
6. WHEN deployed, THE System SHALL serve static files via collectstatic and a web server (Nginx)
7. THE System SHALL pass Django's security check: python manage.py check --deploy

### Requirement 20: Multi-Tenant Scalability

**User Story:** As an Institution Administrator, I want to customize the system for my institution, so that I can meet specific requirements without code changes.

#### Acceptance Criteria

1. THE System SHALL support multiple institutions with separate Department hierarchies
2. THE System SHALL allow each institution to define custom Programs with different duration and credit requirements
3. THE System SHALL store institution-specific student data in StudentProfile.custom_data JSON field
4. WHEN an institution adds a Custom_Registration_Field, THE System SHALL make it available immediately without deployment
5. THE System SHALL support institution-specific grading scales via configuration
6. THE System SHALL allow institutions to configure semester start/end dates independently
7. THE System SHALL maintain data isolation between institutions at the Department level
