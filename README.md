# Academic ERP System

A comprehensive Django REST API backend for managing academic institution operations including user management, academic structure, attendance tracking, examinations, and grading.

## Quick Start

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py runserver
```

## Documentation

See [backend/README.md](backend/README.md) for detailed setup instructions.

## API Documentation

- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Features

- JWT Authentication
- Role-based Access Control
- Academic Management
- Attendance Tracking
- Grading & GPA Calculation
- Communication System
- Audit Logging

## Tech Stack

Django 4.2.28 | Django REST Framework | MySQL | JWT | Swagger
