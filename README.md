# Academic ERP System

A comprehensive, production-ready Django REST API for managing academic institutions with multi-tenant support, built with Django 6.0 and MySQL. Features include student management, faculty operations, attendance tracking, examination system, and automated timetable generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Git

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd academic-erp-system
   ```

2. **Set Up Python Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your settings:
   # - Set SECRET_KEY (generate new one for production)
   # - Configure database credentials
   # - Set DEBUG=True for development
   ```

5. **Set Up Database**
   ```sql
   -- Connect to MySQL and create database
   mysql -u root -p
   CREATE DATABASE academic_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

7. **Seed Demo Data (Optional)**
   ```bash
   python manage.py seed_data
   ```
   This creates demo users, departments, courses, and sample data for testing.

8. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - **Backend API**: http://localhost:8000/api/
   - **Frontend App**: http://localhost:5174/
   - **Swagger Documentation**: http://localhost:8000/swagger/
   - **Admin Panel**: http://localhost:8000/admin/

### Frontend Setup (React + Vite)

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

3. **Start Frontend Development Server**
   ```bash
   npm run dev
   ```

4. **Access Frontend Application**
   - **Frontend**: http://localhost:5174/
   - **Login with demo credentials** (see login page for options)

### Quick Test

Run the demo flow to verify everything works:
```bash
python manage.py test tests.test_demo_flow --verbosity=2
```

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **ReDoc**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Authentication
```bash
# Get JWT Token
POST /api/users/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Use in headers
Authorization: Bearer <your_access_token>
```

### Auto-Generate Timetable
```bash
# Generate timetable for a batch
POST /api/academics/timetable/generate/
{
  "batch_year": 2024,
  "department_id": 1,
  "semester": 3,
  "academic_year": "2026-27"
}

# Get generated timetable
GET /api/academics/timetable/batch/?batch_year=2024&department_id=1&semester=3
```

### Mark Bulk Attendance
```bash
POST /api/attendance/bulk-mark/
{
  "subject_id": 1,
  "date": "2026-03-23",
  "records": [
    {"student_id": 1, "status": "Present"},
    {"student_id": 2, "status": "Absent"}
  ]
}
```

### Get Student Transcript
```bash
GET /api/exams/transcript/1/
# Returns complete transcript with GPA calculation
```

## 🎯 Demo Flow

Run the complete demo test:
```bash
python manage.py test tests.test_demo_flow --verbosity=2
```

This simulates the entire user journey:
1. User Registration (Admin, Faculty, Student)
2. JWT Authentication
3. Academic Structure Creation
4. Faculty Assignment
5. Student Enrollment
6. Attendance Marking

## 🔧 Frontend Integration

The API is configured with CORS support for frontend applications:
- Default allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Configure additional origins in `.env`: `CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com`

## 📁 Project Structure

```
academic-erp-system/
├── backend/                   # Django REST API
│   ├── apps/                 # Django applications
│   │   ├── academics/        # Departments, courses, subjects, timetables
│   │   ├── attendance/       # Attendance management
│   │   ├── common/          # Shared utilities (permissions, exceptions)
│   │   ├── communication/   # Notices and resources
│   │   ├── exams/           # Assessments, grades, transcripts
│   │   ├── faculty/         # Faculty management
│   │   ├── students/        # Student enrollment, academic history
│   │   └── users/           # Authentication, user profiles
│   ├── config/              # Django configuration
│   ├── tests/               # Integration tests
│   ├── requirements.txt     # Python dependencies
│   ├── manage.py           # Django management script
│   └── .env.example        # Environment variables template
├── frontend/                  # React + Vite frontend
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── api.js           # API configuration
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── README.md               # Project documentation
└── .gitignore             # Git ignore rules
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test --verbosity=2

# Run demo flow
python manage.py test tests.test_demo_flow --verbosity=2

# Run final system test
python manage.py test tests.test_final_system --verbosity=2
```

## 🔒 Security Features

- JWT Authentication with refresh tokens
- Role-based permissions (Admin, Faculty, Student)
- Department-level access control
- Audit logging for all API operations
- CORS configuration for secure frontend integration
- Production-ready security settings

## 📊 Key Features

### Core Functionality
- **User Management**: Multi-role authentication system (Admin, Faculty, Student)
- **Academic Structure**: Departments → Courses → Subjects with hierarchical organization
- **Student Management**: Enrollment, semester registration, transcripts, GPA calculation
- **Faculty Management**: Class assignments, subject allocation, attendance marking
- **Attendance System**: Bulk marking with conflict detection and percentage tracking
- **Examination System**: Assessments, grades, automated GPA/CGPA calculation
- **Auto-Generate Timetables**: Intelligent scheduling with conflict detection
- **Communication**: Notice board, resource sharing, file uploads
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

### Multi-Tenant Architecture
- **Dynamic Registration Fields**: Institutions can add custom fields (Aadhar, Passport, etc.) without code changes
- **Flexible Programs**: Configure programs dynamically instead of hardcoded courses
- **Custom Data Storage**: JSONField for institution-specific student data
- **Scalable Design**: Supports multiple institutions with different requirements

### Security & Performance
- JWT Authentication with refresh tokens
- Role-based permissions (RBAC)
- Department-level access control
- Audit logging for all API operations
- CORS configuration for secure frontend integration
- Database query optimization (select_related, prefetch_related)
- Production-ready security settings

## 📈 Database Overview

### Current Seeded Data
- **3 Users**: Admin, Faculty, Student (demo accounts)
- **2 Departments**: Computer Science, Mathematics
- **2 Courses**: B.Tech CS (4 years), M.Sc Math (2 years)
- **3 Subjects**: Data Structures, Algorithm Design, Database Management
- **2 Class Assignments**: Faculty assigned to subjects
- **1 Enrollment**: Student enrolled in B.Tech CS
- **18 Attendance Records**: Demo attendance data

### Database Models (20+ Models)
**Users**: CustomUser, StudentProfile, FacultyProfile, AuditLog  
**Academics**: Department, Course, Program, Subject, Timetable, CustomRegistrationField  
**Students**: Enrollment, SemesterRegistration, FeeTransaction, RegisteredCourse, AcademicHistory  
**Faculty**: ClassAssignment  
**Attendance**: Attendance, AttendanceReportSubmission  
**Exams**: Assessment, Grade, StudentGrade  
**Communication**: Notice, Resource

## 🎯 Demo Credentials

After running `python manage.py seed_data`, use these credentials:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin_demo` | `Admin@2026` |
| **Faculty** | `prof_smith` | `Faculty@2026` |
| **Student** | `john_doe` | `Student@2026` |

## 🚀 Production Deployment

### Quick Deployment Checklist

1. **Generate SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Configure Production Environment**
   ```bash
   SECRET_KEY=your-generated-secret-key
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DB_HOST=your-production-db-host
   DB_NAME=academic_erp_prod
   DB_USER=your-db-user
   DB_PASSWORD=your-secure-password
   ```

3. **Run Security Check**
   ```bash
   python manage.py check --deploy
   ```

4. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Set Up Web Server**
   - Use Nginx as reverse proxy
   - Run with Gunicorn: `gunicorn config.wsgi:application`
   - Configure SSL/TLS with Let's Encrypt

6. **Database Optimization**
   - Add indexes for frequently queried fields
   - Set up automated backups
   - Configure connection pooling

7. **Monitoring**
   - Set up application logging
   - Configure health check endpoints
   - Monitor database performance

For detailed deployment instructions, see `backend/DEPLOYMENT.md`

## 🔐 Multi-Tenant Features

### Custom Registration Fields

Institutions can add custom fields dynamically:

```python
from apps.academics.models import CustomRegistrationField

CustomRegistrationField.objects.create(
    field_name='aadhar_number',
    field_label='Aadhar Number',
    field_type='text',
    is_required=True,
    placeholder='1234-5678-9012',
    order=1
)
```

**API Endpoint**: `GET /api/academics/custom-fields/active_fields/`

### Dynamic Programs

Configure academic programs per institution:

```python
from apps.academics.models import Program

Program.objects.create(
    name='Bachelor of Technology',
    code='BTECH',
    department=cs_dept,
    duration_years=4,
    total_credits=160
)
```

**API Endpoint**: `GET /api/academics/programs/`

### Student Custom Data

Store institution-specific data in JSONField:

```json
{
  "custom_data": {
    "aadhar_number": "1234-5678-9012",
    "blood_group": "O+",
    "parent_phone": "+91-9876543210"
  }
}
```

## 📄 License

This project is licensed under the MIT License.

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework 3.14+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: MySQL 8.0+ (PostgreSQL compatible)
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Testing**: Django TestCase with 50+ test cases

### Frontend
- **Framework**: React 18+ with Vite 4+
- **Routing**: React Router 6+
- **HTTP Client**: Axios
- **Styling**: CSS3 with CSS Variables
- **Features**: Dark/Light mode, Responsive design, Role-based layouts

### Development Tools
- Python 3.11+
- Node.js 16+
- Git version control
- VS Code (recommended)

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: April 2026