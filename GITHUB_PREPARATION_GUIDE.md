# GitHub Preparation Guide - Academic ERP Backend

## 🎯 Current Status
Your project is restructured and ready for GitHub with minimal cleanup needed.

---

## ✅ Step-by-Step GitHub Preparation

### Step 1: Clean Up Unnecessary Files

#### Delete the Portal App (Legacy/Unused)
```bash
# Navigate to backend directory
cd backend

# Delete the portal app
rmdir /s /q apps\portal
```

#### Delete Python Cache Files
```bash
# Delete all __pycache__ directories
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# Delete .pyc files
del /s /q *.pyc
```

#### Delete Test Upload Files (Optional)
```bash
# Delete test PDF files
rmdir /s /q resources\2026
```

---

### Step 2: Create/Update Essential Files

#### A. Create `.env.example` (Template for Environment Variables)
Already exists at `backend/.env.example.txt` - Good!

#### B. Update README.md
The README should include:
- Project description
- Installation instructions
- Configuration steps
- API documentation link
- Running instructions

#### C. Verify .gitignore
Already exists at `backend/.gitignore` - Good!

---

### Step 3: Security Check

#### Remove Sensitive Data from settings.py
⚠️ **CRITICAL**: Your `backend/config/settings.py` contains:
- Database password: `Krishna@2210`
- Secret key: `django-insecure-r3_0@ab0(k1a6d1x5vppqz@o9qdxvr(3!z86o_qm0i_o$u4g1^`

**Action Required:**
1. Move these to environment variables
2. Update settings.py to read from environment
3. Never commit the actual `.env` file

---

### Step 4: Initialize Git Repository

```bash
# Navigate to project root
cd C:\NVJKA\NVJKA\NVJKA

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Academic ERP Backend System"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

---

## 🔒 CRITICAL: Secure Your Settings Before Upload

### Option 1: Use Environment Variables (Recommended)

1. **Install python-decouple**:
```bash
pip install python-decouple
```

2. **Create `.env` file** (in backend/ directory):
```env
SECRET_KEY=django-insecure-r3_0@ab0(k1a6d1x5vppqz@o9qdxvr(3!z86o_qm0i_o$u4g1^
DEBUG=True
DB_NAME=academic_erp
DB_USER=root
DB_PASSWORD=Krishna@2210
DB_HOST=localhost
DB_PORT=3306
```

3. **Update `backend/config/settings.py`**:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

4. **Update `.env.example.txt`**:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=academic_erp
DB_USER=root
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
```

5. **Verify `.gitignore` includes**:
```
.env
*.env
```

### Option 2: Manual Replacement (Quick Fix)

Replace sensitive values in `settings.py` with placeholders:
```python
SECRET_KEY = 'REPLACE_WITH_YOUR_SECRET_KEY'
'PASSWORD': 'REPLACE_WITH_YOUR_DB_PASSWORD',
```

Then document in README that users need to update these values.

---

## 📝 Files to Include in GitHub

### ✅ Include These:
- All `.py` files (source code)
- All `.md` files (documentation)
- `requirements.txt`
- `manage.py`
- `.gitignore`
- `.env.example.txt` (template only)
- All `migrations/` folders
- All `tests/` folders
- Empty `resources/` folder (for uploads)

### ❌ Exclude These (via .gitignore):
- `.env` (actual secrets)
- `__pycache__/` folders
- `*.pyc` files
- `db.sqlite3`
- `media/` and `resources/` with files
- `.vscode/`, `.idea/`
- Virtual environment folders

---

## 📋 Pre-Upload Checklist

- [ ] Delete `apps/portal/` directory
- [ ] Delete all `__pycache__/` directories
- [ ] Delete test upload files in `resources/`
- [ ] Secure sensitive data in `settings.py`
- [ ] Update `README.md` with setup instructions
- [ ] Verify `.gitignore` is correct
- [ ] Test that project still works after cleanup
- [ ] Create `.env.example.txt` with placeholders
- [ ] Add `python-decouple` to `requirements.txt`

---

## 🚀 Recommended README.md Structure

```markdown
# Academic ERP Backend System

A comprehensive Django REST API for managing academic institution operations.

## Features
- JWT Authentication
- Role-based Access Control (Admin, Faculty, Student)
- Academic Structure Management
- Student Enrollment System
- Attendance Tracking
- Examination & Grading
- GPA Calculation
- Communication System (Notices & Resources)
- Audit Logging

## Tech Stack
- Django 4.2.28
- Django REST Framework
- MySQL Database
- JWT Authentication
- Swagger/OpenAPI Documentation

## Installation

1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Configure database
5. Run migrations
6. Start server

## API Documentation
Access Swagger UI at: `http://localhost:8000/swagger/`

## License
MIT License
```

---

## 🎯 Quick Commands Summary

```bash
# 1. Clean up
cd backend
rmdir /s /q apps\portal
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# 2. Secure settings (install decouple)
pip install python-decouple
# Then update settings.py as shown above

# 3. Update requirements
pip freeze > requirements.txt

# 4. Git operations
cd ..
git init
git add .
git commit -m "Initial commit: Academic ERP Backend"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

---

## ⚠️ IMPORTANT WARNINGS

1. **NEVER commit `.env` file** - Contains passwords and secrets
2. **NEVER commit database files** - Already in .gitignore
3. **NEVER commit `__pycache__`** - Already in .gitignore
4. **ALWAYS use environment variables** - For sensitive data
5. **ALWAYS test after cleanup** - Run `python manage.py check`

---

## 📊 What Will Be Uploaded

**Approximate File Count:**
- Python source files: ~50
- Migration files: ~30
- Test files: ~20
- Documentation files: ~15
- Configuration files: ~10

**Total Size:** ~2-3 MB (without cache and uploads)

---

## ✅ Final Verification

Before pushing to GitHub, run:

```bash
cd backend
python manage.py check
python manage.py test
```

Both should pass without errors.

---

**Last Updated:** February 13, 2026  
**Status:** Ready for GitHub with security updates needed
