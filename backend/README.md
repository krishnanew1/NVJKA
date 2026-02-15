# Academic ERP Backend

## Overview
A modular Academic ERP backend built using Django and Django REST Framework.

## Modules
- Students
- Faculty
- Attendance
- Exams
- GPA Calculation
- Timetable Conflict Detection

## Tech Stack
- Django
- Django REST Framework
- SQLite / PostgreSQL

## Setup Instructions

1. Clone the repo
2. Create virtual environment
3. Install dependencies
4. Run migrations
5. Start server

python -m venv venv
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
