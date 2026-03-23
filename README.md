# Academic ERP System

A comprehensive Django REST API for managing academic institutions, built with Django 6.0 and MySQL.

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

7. **Create Superuser Account**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - **API Base**: http://localhost:8000/api/
   - **Swagger Documentation**: http://localhost:8000/swagger/
   - **Admin Panel**: http://localhost:8000/admin/

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

- **User Management**: Multi-role authentication system
- **Academic Structure**: Departments → Courses → Subjects
- **Student Management**: Enrollment, transcripts, GPA calculation
- **Faculty Management**: Class assignments, subject allocation
- **Attendance System**: Bulk marking with conflict detection
- **Examination System**: Assessments, grades, automated GPA
- **Auto-Generate Timetables**: Intelligent scheduling with conflict detection
- **Communication**: Notice board, resource sharing
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## 🚀 Production Deployment

See [DEPLOYMENT.md](backend/DEPLOYMENT.md) for detailed production setup instructions including:
- Security configuration
- Database optimization
- Web server setup (Nginx + Gunicorn)
- SSL/TLS configuration
- Monitoring and logging

## 📄 License

This project is licensed under the MIT License.