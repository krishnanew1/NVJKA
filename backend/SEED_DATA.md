# Database Seed Data

This document describes the demo data seeding functionality for the Academic ERP system.

## Overview

The `seed_data` management command creates demo users, departments, courses, subjects, and class assignments for testing and demonstration purposes.

## Usage

To seed the database with demo data, run:

```bash
python manage.py seed_data
```

## What Gets Created

### Departments
- **Computer Science (CS)**: Department of Computer Science and Engineering
- **Mathematics (MATH)**: Department of Mathematics

### Courses
- **BTECH-CS**: Bachelor of Technology in Computer Science
  - Department: Computer Science
  - Duration: 4 years
  - Credits: 160

- **MSC-MATH**: Master of Science in Mathematics
  - Department: Mathematics
  - Duration: 2 years
  - Credits: 80

### Subjects
- **CS101 - Data Structures**
  - Course: BTECH-CS
  - Semester: 3
  - Credits: 4
  - Type: Mandatory

- **CS201 - Algorithm Design**
  - Course: BTECH-CS
  - Semester: 4
  - Credits: 4
  - Type: Mandatory

- **CS301 - Database Management Systems**
  - Course: BTECH-CS
  - Semester: 5
  - Credits: 4
  - Type: Mandatory

### Users

#### Admin User
- **Username**: `admin_demo`
- **Password**: `Admin@2026`
- **Role**: ADMIN
- **Permissions**: Full system access, superuser privileges

#### Faculty User
- **Username**: `prof_smith`
- **Password**: `Faculty@2026`
- **Role**: FACULTY
- **Profile**:
  - Employee ID: FAC001
  - Department: Computer Science
  - Designation: Associate Professor
  - Specialization: Data Structures and Algorithms
  - Date of Joining: 2020-01-15

**Class Assignments**:
- CS101 - Data Structures (Semester 3, Academic Year 2026)
- CS201 - Algorithm Design (Semester 4, Academic Year 2026)

#### Student User
- **Username**: `john_doe`
- **Password**: `Student@2026`
- **Role**: STUDENT
- **Profile**:
  - Enrollment Number: STU2023001
  - Department: Computer Science
  - Current Semester: 3
  - Batch Year: 2023

**Enrollments**:
- BTECH-CS (Bachelor of Technology in Computer Science)
  - Semester: 3
  - Status: Active

## Features

### Safe Creation
- Uses `get_or_create()` to prevent duplicate entries
- Wrapped in a database transaction for atomicity
- Shows warnings for existing records instead of errors

### Idempotent
- Can be run multiple times safely
- Won't create duplicate data
- Updates existing records if needed

### Comprehensive
- Creates complete data hierarchy (departments → courses → subjects)
- Links users to their profiles (faculty/student)
- Creates realistic class assignments and enrollments

## Testing the System

After running the seed command, you can:

1. **Login as Admin** (`admin_demo` / `Admin@2026`)
   - View and manage all departments, courses, and subjects
   - Create new class assignments
   - Manage faculty and student profiles

2. **Login as Faculty** (`prof_smith` / `Faculty@2026`)
   - View assigned classes (CS101 and CS201)
   - Mark attendance for enrolled students
   - Access faculty-specific features

3. **Login as Student** (`john_doe` / `Student@2026`)
   - View enrolled courses
   - Check timetable
   - View attendance and grades

## Troubleshooting

### Command Not Found
If you get a "command not found" error, make sure:
- You're in the `backend` directory
- The virtual environment is activated
- Django is properly installed

### Database Errors
If you encounter database errors:
- Make sure migrations are up to date: `python manage.py migrate`
- Check database connection settings in `config/settings.py`

### Duplicate Key Errors
If you get duplicate key errors:
- The command is designed to handle duplicates gracefully
- Check the output for warnings about existing records
- If needed, you can manually delete records and re-run

## Resetting Data

To completely reset and reseed the database:

```bash
# Delete the database (SQLite)
rm db.sqlite3

# Run migrations
python manage.py migrate

# Seed data
python manage.py seed_data
```

## Extending the Seed Data

To add more demo data, edit `apps/academics/management/commands/seed_data.py`:

1. Add new departments, courses, or subjects
2. Create additional users with different roles
3. Add more class assignments or enrollments
4. Follow the existing pattern using `get_or_create()`

## Notes

- All passwords follow the format: `{Role}@2026`
- Phone numbers are dummy values for demonstration
- Email addresses use `@example.com` domain
- Academic year is set to 2026 for all assignments
- All data is for demonstration purposes only
