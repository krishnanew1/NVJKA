# 🎓 Academic ERP Backend System

A comprehensive Django REST API backend for managing academic institution operations including user management, academic structure, student enrollment, attendance tracking, examinations, grading, and communication systems.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [License](#license)

---

## ✨ Features

### Core Functionality
- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Admin, Faculty, and Student roles
- **User Management** - Custom user model with automatic profile creation
- **Academic Structure Management** - Departments, Courses, Subjects, and Timetables
- **Student Enrollment System** - Course registration and academic history tracking
- **Faculty Management** - Class assignments and roster management
- **Attendance Tracking** - Bulk attendance marking with percentage calculations
- **Examination & Grading** - Assessment management with grade validation
- **GPA Calculation** - Credit-weighted GPA calculation (10.0 scale)
- **Communication System** - Notice board and learning resource management
- **Audit Logging** - Comprehensive request logging for all data modifications
- **API Documentation** - Interactive Swagger/ReDoc documentation

### Key Highlights
- ✅ 184 automated tests (100% passing)
- ✅ Timetable conflict prevention
- ✅ Automatic profile creation via Django signals
- ✅ Nested serialization for related data
- ✅ Bulk operations with transaction safety
- ✅ File upload with validation
- ✅ Sensitive data sanitization in logs

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.14+ | Programming Language |
| Django | 4.2.28 | Web Framework |
| Django REST Framework | 3.16.1 | REST API Toolkit |
| MySQL | 8.0+ | Database |
| Simple JWT | 5.5.1 | JWT Authentication |
| drf-yasg | 1.21.14 | API Documentation |
| python-decouple | 3.8 | Environment Variables |

---

## 📁 Project Structure

```
academic-erp-backend/
├── backend/
│   ├── apps/                      # Django applications
│   │   ├── academics/            # Academic structure (Departments, Courses, Subjects, Timetables)
│   │   ├── attendance/           # Attendance tracking and calculations
│   │   ├── communication/        # Notices and learning resources
│   │   ├── exams/               # Examinations, grading, and GPA calculation
│   │   ├── faculty/             # Faculty management and class assignments
│   │   ├── students/            # Student enrollment and academic history
│   │   └── users/               # Authentication, user profiles, and audit logging
│   ├── config/                   # Project configuration
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # URL routing
│   │   ├── middleware.py        # Custom middleware (audit logging)
│   │   └── wsgi.py              # WSGI configuration
│   ├── docs/                     # Technical documentation
│   ├── resources/                # Uploaded files storage
│   ├── manage.py                 # Django management script
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── .gitignore               # Git ignore rules
└── README.md                     # This file
```

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.14 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/academic-erp-backend.git
cd academic-erp-backend/backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file and update the following:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=academic_erp
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306
```

**Generate a new SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Create MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE academic_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## 🏃 Running the Application

### Start Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **API Base URL**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
  - Interactive API explorer
  - Test endpoints directly from browser
  - JWT authentication support

- **ReDoc**: http://127.0.0.1:8000/redoc/
  - Clean, responsive documentation
  - Better for reading and reference

### Authentication

Most endpoints require JWT authentication:

1. **Get Token**: POST to `/api/auth/login/` with username and password
2. **Use Token**: Add to request headers:
   ```
   Authorization: Bearer <your_access_token>
   ```
3. **Refresh Token**: POST to `/api/auth/token/refresh/` with refresh token

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

**Expected Output**: 184 tests passing

### Run Specific App Tests

```bash
python manage.py test apps.users
python manage.py test apps.academics
python manage.py test apps.attendance
```

### Check for Issues

```bash
python manage.py check
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | JWT token generation | No |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |
| GET | `/api/auth/dashboard/student/` | Student dashboard | Yes |
| GET | `/api/auth/dashboard/faculty/` | Faculty dashboard | Yes |

### Academic Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET/POST | `/api/academics/departments/` | List/Create departments | Yes |
| GET/PUT/DELETE | `/api/academics/departments/{id}/` | Retrieve/Update/Delete department | Yes |
| GET/POST | `/api/academics/courses/` | List/Create courses | Yes |
| GET/PUT/DELETE | `/api/academics/courses/{id}/` | Retrieve/Update/Delete course | Yes |
| GET/POST | `/api/academics/subjects/` | List/Create subjects | Yes |
| GET/PUT/DELETE | `/api/academics/subjects/{id}/` | Retrieve/Update/Delete subject | Yes |
| GET/POST | `/api/academics/timetables/` | List/Create timetables | Yes |
| GET/PUT/DELETE | `/api/academics/timetables/{id}/` | Retrieve/Update/Delete timetable | Yes |

### Student Operations
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/students/enroll/` | Enroll student in course | Yes (Admin) |

### Attendance
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/attendance/bulk-mark/` | Mark attendance for multiple students | Yes |

### Documentation
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/swagger/` | Swagger UI documentation | No |
| GET | `/redoc/` | ReDoc documentation | No |
| GET | `/swagger.json` | OpenAPI schema (JSON) | No |
| GET | `/swagger.yaml` | OpenAPI schema (YAML) | No |

---

## 🔐 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Django's built-in password hashing
- **Role-Based Permissions** - Admin, Faculty, Student access levels
- **CSRF Protection** - Enabled by default
- **Audit Logging** - All data modifications logged
- **Environment Variables** - Sensitive data in .env file
- **Input Validation** - Serializer and model-level validation

---

## 📖 Additional Documentation

Technical documentation is available in the `backend/docs/` directory:

- `API_DOCUMENTATION_SETUP.md` - Swagger configuration guide
- `ATTENDANCE_CALCULATIONS_DOCUMENTATION.md` - Attendance calculation logic
- `AUDIT_LOGGING_DOCUMENTATION.md` - Audit system implementation
- `ENROLLMENT_API_DOCUMENTATION.md` - Enrollment endpoint details
- `TIMETABLE_CONFLICT_PREVENTION.md` - Conflict detection logic
- `attendance.md` - Attendance system overview
- `faculty.md` - Faculty management details
- `gpa.md` - GPA calculation algorithms

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 📧 Support

For questions, issues, or support:
- Open an issue on GitHub
- Check the documentation in `backend/docs/`
- Review the API documentation at `/swagger/`

---

## 🎯 Project Status

- ✅ Backend Development: Complete
- ✅ API Documentation: Complete
- ✅ Testing: 184 tests passing
- ✅ Security: Environment variables configured
- ✅ Production Ready: Yes

---

**Built with ❤️ using Django and Django REST Framework**
