# Academic ERP Backend System

A comprehensive Django REST API for managing academic institution operations.

## Features

- JWT Authentication with role-based access control
- User Management (Admin, Faculty, Student)
- Academic Structure (Departments, Courses, Subjects, Timetables)
- Student Enrollment System
- Attendance Tracking with bulk marking
- Examination & Grading System
- GPA Calculation (10.0 scale)
- Communication System (Notices & Resources)
- Audit Logging
- API Documentation (Swagger/ReDoc)

## Tech Stack

- Django 4.2.28
- Django REST Framework
- MySQL Database
- JWT Authentication
- Swagger/OpenAPI Documentation

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
copy .env.example .env
# Edit .env and update SECRET_KEY and DB_PASSWORD
```

5. **Create MySQL database**
```sql
CREATE DATABASE academic_erp;
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Run server**
```bash
python manage.py runserver
```

## API Documentation

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- Admin Panel: http://localhost:8000/admin/

## Key Endpoints

- `POST /api/auth/login/` - JWT authentication
- `GET /api/auth/dashboard/student/` - Student dashboard
- `GET /api/auth/dashboard/faculty/` - Faculty dashboard
- `/api/academics/` - Academic management
- `/api/students/` - Student operations
- `/api/attendance/` - Attendance tracking

## Testing

```bash
python manage.py test
```

## Project Structure

```
backend/
├── apps/                 # Django applications
│   ├── academics/       # Academic structure
│   ├── attendance/      # Attendance tracking
│   ├── communication/   # Notices & resources
│   ├── exams/          # Examinations & grading
│   ├── faculty/        # Faculty management
│   ├── students/       # Student enrollment
│   └── users/          # Authentication
├── config/              # Project configuration
├── docs/               # Documentation
└── manage.py           # Django management
```

## License

MIT License
