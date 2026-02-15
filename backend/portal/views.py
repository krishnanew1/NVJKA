from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Enrollment, Attendance

# 1. The Home View (Landing Page)
def home(request):
    return render(request, 'portal/home.html')

# 2. The Student Dashboard View
@login_required(login_url='/admin/login/') 
def student_dashboard(request):
    user = request.user
    
    # Default values
    courses_count = 0
    attendance_percent = 0
    
    # Only fetch real data if the user is a Student
    if user.role == 'Student':
        courses_count = Enrollment.objects.filter(student=user, status='Verified').count()
        
        total_classes = Attendance.objects.filter(student=user).count()
        present_count = Attendance.objects.filter(student=user, status='Present').count()
        
        if total_classes > 0:
            attendance_percent = round((present_count / total_classes) * 100)
    
    context = {
        'student': user,
        'courses_count': courses_count,
        'attendance_percent': attendance_percent,
    }
    
    return render(request, 'portal/student_dashboard.html', context)