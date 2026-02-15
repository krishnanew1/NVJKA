# 🚀 GitHub Upload Checklist - DO THIS BEFORE UPLOADING

## ⚠️ CRITICAL: Security Issues Found!

Your `backend/config/settings.py` contains:
- **Database Password**: `Krishna@2210`
- **Secret Key**: `django-insecure-r3_0@ab0(k1a6d1x5vppqz@o9qdxvr(3!z86o_qm0i_o$u4g1^`

**These MUST be secured before uploading to GitHub!**

---

## 📋 Step-by-Step Instructions

### Step 1: Clean Up Files (5 minutes)

Open Command Prompt in your project root and run:

```cmd
cd backend

REM Delete portal app (unused)
rmdir /s /q apps\portal

REM Delete Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc

REM Delete test uploads (optional)
rmdir /s /q resources\2026
```

---

### Step 2: Secure Your Settings (10 minutes)

#### Option A: Quick Fix (Easiest)

1. Open `backend/config/settings.py`

2. Replace line 24:
```python
# OLD:
SECRET_KEY = 'django-insecure-r3_0@ab0(k1a6d1x5vppqz@o9qdxvr(3!z86o_qm0i_o$u4g1^'

# NEW:
SECRET_KEY = 'your-secret-key-here-change-this-in-production'
```

3. Replace line 102:
```python
# OLD:
'PASSWORD': 'Krishna@2210',

# NEW:
'PASSWORD': 'your-database-password',
```

4. Add a note in README.md:
```markdown
## Configuration
1. Update `SECRET_KEY` in `backend/config/settings.py`
2. Update database password in `backend/config/settings.py`
```

#### Option B: Environment Variables (Best Practice)

1. Install python-decouple:
```cmd
cd backend
pip install python-decouple
pip freeze > requirements.txt
```

2. Create `backend/.env` file:
```env
SECRET_KEY=django-insecure-r3_0@ab0(k1a6d1x5vppqz@o9qdxvr(3!z86o_qm0i_o$u4g1^
DEBUG=True
DB_NAME=academic_erp
DB_USER=root
DB_PASSWORD=Krishna@2210
DB_HOST=localhost
DB_PORT=3306
```

3. Update `backend/config/settings.py`:

Add at the top (after imports):
```python
from decouple import config
```

Replace line 24:
```python
SECRET_KEY = config('SECRET_KEY')
```

Replace line 27:
```python
DEBUG = config('DEBUG', default=False, cast=bool)
```

Replace lines 97-106:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='academic_erp'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}
```

4. Update `backend/.env.example.txt`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=academic_erp
DB_USER=root
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
```

5. Verify `backend/.gitignore` includes:
```
.env
*.env
```

---

### Step 3: Update README (5 minutes)

Create a comprehensive `backend/README.md`:

```markdown
# Academic ERP Backend System

A comprehensive Django REST API for managing academic institution operations including user management, academic structure, attendance tracking, examinations, and grading.

## 🎯 Features

- **Authentication**: JWT-based authentication with role-based access control
- **User Management**: Admin, Faculty, and Student roles with automatic profile creation
- **Academic Structure**: Departments, Courses, Subjects, and Timetables with conflict prevention
- **Student Management**: Enrollment tracking and academic history
- **Faculty Management**: Class assignments and roster management
- **Attendance System**: Bulk attendance marking with percentage calculations
- **Examination & Grading**: Assessment management with GPA calculation (10.0 scale)
- **Communication**: Notice board and learning resource management
- **Audit Logging**: Comprehensive request logging for all data modifications
- **API Documentation**: Interactive Swagger/ReDoc documentation

## 🛠️ Tech Stack

- **Framework**: Django 4.2.28
- **API**: Django REST Framework 3.16.1
- **Authentication**: Simple JWT
- **Database**: MySQL
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Python**: 3.14

## 📦 Installation

### Prerequisites
- Python 3.14+
- MySQL Server
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/academic-erp-backend.git
cd academic-erp-backend/backend
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
# Copy the example file
copy .env.example.txt .env

# Edit .env and update:
# - SECRET_KEY (generate a new one)
# - DB_PASSWORD (your MySQL password)
# - Other settings as needed
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

8. **Run development server**
```bash
python manage.py runserver
```

9. **Access the application**
- API: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Expected: 184 tests passing

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### Key Endpoints

**Authentication**
- `POST /api/auth/login/` - JWT token generation
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/dashboard/student/` - Student dashboard
- `GET /api/auth/dashboard/faculty/` - Faculty dashboard

**Academic Management**
- `/api/academics/departments/` - Department CRUD
- `/api/academics/courses/` - Course CRUD
- `/api/academics/subjects/` - Subject CRUD
- `/api/academics/timetables/` - Timetable CRUD

**Student Operations**
- `POST /api/students/enroll/` - Enroll student in course

**Attendance**
- `POST /api/attendance/bulk-mark/` - Bulk attendance marking

## 🏗️ Project Structure

```
backend/
├── apps/                      # Django applications
│   ├── academics/            # Academic structure management
│   ├── attendance/           # Attendance tracking
│   ├── communication/        # Notices and resources
│   ├── exams/               # Examinations and grading
│   ├── faculty/             # Faculty management
│   ├── students/            # Student enrollment
│   └── users/               # Authentication and profiles
├── config/                   # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── middleware.py        # Custom middleware
│   └── wsgi.py              # WSGI configuration
├── docs/                     # Documentation
├── resources/                # Uploaded files storage
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔒 Security

- JWT authentication for all API endpoints
- Role-based access control (Admin, Faculty, Student)
- Password validation and hashing
- Audit logging for all data modifications
- CSRF protection enabled

## 📝 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.
```

---

### Step 4: Verify Everything Works (5 minutes)

```cmd
cd backend

REM Check for issues
python manage.py check

REM Run tests (optional but recommended)
python manage.py test
```

Both should pass without errors.

---

### Step 5: Initialize Git and Push (5 minutes)

```cmd
REM Navigate to project root
cd C:\NVJKA\NVJKA\NVJKA

REM Initialize git (if not already done)
git init

REM Add all files
git add .

REM Check what will be committed
git status

REM Create initial commit
git commit -m "Initial commit: Academic ERP Backend System"

REM Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

REM Push to GitHub
git branch -M main
git push -u origin main
```

---

## ✅ Final Checklist

Before pushing to GitHub, verify:

- [ ] Deleted `apps/portal/` directory
- [ ] Deleted all `__pycache__/` directories
- [ ] Deleted test files in `resources/`
- [ ] Secured `SECRET_KEY` in settings.py
- [ ] Secured database `PASSWORD` in settings.py
- [ ] Created/updated `.env.example.txt`
- [ ] Updated `README.md` with setup instructions
- [ ] Verified `.gitignore` excludes `.env`
- [ ] Ran `python manage.py check` (passes)
- [ ] Tested that project still works
- [ ] Created GitHub repository
- [ ] Ready to push!

---

## 📊 What Will Be Uploaded

**Files to be uploaded:**
- ✅ All Python source code (~50 files)
- ✅ All migrations (~30 files)
- ✅ All tests (~20 files)
- ✅ All documentation (~15 files)
- ✅ Configuration files
- ✅ requirements.txt
- ✅ .gitignore
- ✅ .env.example.txt (template only)

**Files excluded (via .gitignore):**
- ❌ .env (your actual secrets)
- ❌ __pycache__/ folders
- ❌ *.pyc files
- ❌ Database files
- ❌ Uploaded media files
- ❌ IDE settings

**Estimated upload size:** 2-3 MB

---

## ⚠️ IMPORTANT REMINDERS

1. **NEVER commit the `.env` file** - It contains your passwords!
2. **ALWAYS use `.env.example.txt`** - As a template for others
3. **TEST before pushing** - Run `python manage.py check`
4. **Document configuration** - In README.md
5. **Keep secrets secret** - Use environment variables

---

## 🆘 Need Help?

If you encounter issues:
1. Check that `.gitignore` is working: `git status`
2. Verify no sensitive data: Review files before commit
3. Test locally: `python manage.py check`
4. Check documentation: See `GITHUB_PREPARATION_GUIDE.md`

---

**Ready to upload?** Follow the steps above in order!

**Estimated time:** 30 minutes total
