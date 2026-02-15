from django.db import models
from django.conf import settings

# 1. Departments Table
class Department(models.Model):
    dept_name = models.CharField(max_length=100, unique=True)
    dept_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.dept_name

# 3. Student Profiles
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    dob = models.DateField(null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    parent_contact = models.CharField(max_length=15, null=True, blank=True)
    family_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    aadhar_no = models.CharField(max_length=12, unique=True, null=True, blank=True)
    abc_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Financial/Hostel Info
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_account_no = models.CharField(max_length=20, null=True, blank=True)
    hostel_name = models.CharField(max_length=50, null=True, blank=True)
    room_no = models.CharField(max_length=10, null=True, blank=True)
    scholarship_eligible = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.user.username}"

# 4. Faculty Profiles
class FacultyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    designation = models.CharField(max_length=50, null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} ({self.designation})"

# 5. Courses Table
class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    credits = models.IntegerField(default=4)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    syllabus_url = models.CharField(max_length=255, null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return self.course_code

# 6. Faculty Assignments
class FacultyAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    semester_no = models.IntegerField()
    academic_year = models.CharField(max_length=10)
    section = models.CharField(max_length=5)

# 7. Enrollments
class Enrollment(models.Model):
    STATUS_CHOICES = (('Pending', 'Pending'), ('Verified', 'Verified'), ('Rejected', 'Rejected'))
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester_no = models.IntegerField()
    is_backlog = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

# 8. Attendance
class Attendance(models.Model):
    STATUS_CHOICES = (('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late'))

    assignment = models.ForeignKey(FacultyAssignment, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')

# 10. Fee Payments
class FeePayment(models.Model):
    PAYMENT_STATUS = (('Successful', 'Successful'), ('Failed', 'Failed'), ('Pending', 'Pending'))

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='Pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)