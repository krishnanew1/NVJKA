from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsDepartmentHead
from .models import (
    Enrollment, AcademicHistory, SemesterRegistration,
    FeeTransaction, RegisteredCourse
)
from .serializers import (
    EnrollmentSerializer, AcademicHistorySerializer,
    SemesterRegistrationSerializer
)


class IsAdminOrFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'FACULTY')


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for student ``Enrollment`` records.

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
      Students are automatically scoped to their own enrollments;
      Admin and Faculty see all records.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head (same department as the student).

    **Filters** (via query params)

    Standard DRF filtering is available on all fields exposed by the serializer.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return Enrollment.objects.filter(
                student__user=user
            ).select_related('course', 'student', 'student__user', 'student__department')
        return Enrollment.objects.all().select_related('course', 'student', 'student__user', 'student__department')

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)


class AcademicHistoryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for student ``AcademicHistory`` records.

    Stores prior academic credentials (school/college, board, year, grade).

    **Permissions**

    - ``list`` / ``retrieve``: any authenticated user.
      Students are scoped to their own history; Admin and Faculty see all.
    - ``create`` / ``update`` / ``partial_update``: Admin or Faculty only.
    - ``destroy``: Admin or Department Head (same department as the student).
    """
    serializer_class = AcademicHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return AcademicHistory.objects.filter(student__user=user)
        return AcademicHistory.objects.all()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsDepartmentHead()]
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAdminOrFaculty()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()  # triggers has_object_permission
        return super().destroy(request, *args, **kwargs)



class SemesterRegistrationViewSet(viewsets.ModelViewSet):
    """
    CRUD API for student semester registrations.
    
    **Permissions**
    
    - Students can only view and create their own registrations
    - Admin and Faculty can view all registrations
    - Only Admin can update/delete registrations
    
    **Endpoints**
    
    - POST /api/students/semester-register/ - Create new semester registration
    - GET /api/students/semester-register/ - List registrations (filtered by user role)
    - GET /api/students/semester-register/{id}/ - Retrieve specific registration
    - PUT/PATCH /api/students/semester-register/{id}/ - Update registration (Admin only)
    - DELETE /api/students/semester-register/{id}/ - Delete registration (Admin only)
    """
    serializer_class = SemesterRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """
        Filter queryset based on user role.
        
        Students see only their own registrations.
        Admin and Faculty see all registrations.
        """
        user = self.request.user
        
        if user.role == 'STUDENT':
            # Students can only see their own registrations
            return SemesterRegistration.objects.filter(
                student__user=user
            ).prefetch_related('fee_transactions', 'registered_courses__subject')
        
        # Admin and Faculty can see all registrations
        return SemesterRegistration.objects.all().select_related(
            'student__user', 'student__program'
        ).prefetch_related('fee_transactions', 'registered_courses__subject')
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        - list, retrieve, create: Any authenticated user
        - update, partial_update, destroy: Admin only
        """
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Create semester registration for the logged-in student.
        
        Automatically sets the student field to the current user's student profile.
        """
        user = self.request.user
        
        # Ensure user is a student
        if user.role != 'STUDENT':
            raise PermissionDenied('Only students can create semester registrations.')
        
        # Get the student profile
        try:
            student_profile = user.student_profile
        except AttributeError:
            raise PermissionDenied('Student profile not found for this user.')
        
        # Save with the current student
        serializer.save(student=student_profile)



from rest_framework.views import APIView
from apps.users.models import StudentProfile


class RegistrationTrackingView(APIView):
    """
    Admin API endpoint to track semester registration status.
    
    **Permissions**: Admin only
    
    **Query Parameters**:
    - academic_year (required): e.g., '2025-26'
    - semester (required): e.g., 'Jan-Jun 2026'
    
    **Response**:
    Returns a list of all students with their registration status:
    - reg_no: Student registration number
    - name: Student full name
    - program: Program name and code
    - has_registered: Boolean indicating if student has registered
    - registration_id: ID of the registration (if exists)
    
    **Example**:
    GET /api/students/registration-tracking/?academic_year=2025-26&semester=Jan-Jun 2026
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Get query parameters
        academic_year = request.query_params.get('academic_year')
        semester = request.query_params.get('semester')
        
        # Validate required parameters
        if not academic_year or not semester:
            return Response(
                {
                    'error': 'Both academic_year and semester query parameters are required',
                    'example': '/api/students/registration-tracking/?academic_year=2025-26&semester=Jan-Jun 2026'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch all students
        students = StudentProfile.objects.select_related(
            'user', 'program', 'department'
        ).all()
        
        # Build response data
        tracking_data = []
        for student in students:
            # Check if student has registered for this semester
            registration = SemesterRegistration.objects.filter(
                student=student,
                academic_year=academic_year,
                semester=semester
            ).first()
            
            tracking_data.append({
                'id': student.id,
                'reg_no': student.reg_no or student.enrollment_number,
                'name': student.user.get_full_name() or student.user.username,
                'email': student.user.email,
                'program': {
                    'name': student.program.name if student.program else 'N/A',
                    'code': student.program.code if student.program else 'N/A'
                },
                'department': {
                    'name': student.department.name if student.department else 'N/A',
                    'code': student.department.code if student.department else 'N/A'
                },
                'current_semester': student.current_semester,
                'batch_year': student.batch_year,
                'has_registered': registration is not None,
                'registration_id': registration.id if registration else None,
                'registration_date': registration.created_at.isoformat() if registration else None
            })
        
        # Calculate summary statistics
        total_students = len(tracking_data)
        registered_count = sum(1 for s in tracking_data if s['has_registered'])
        pending_count = total_students - registered_count
        registration_percentage = (registered_count / total_students * 100) if total_students > 0 else 0
        
        return Response({
            'academic_year': academic_year,
            'semester': semester,
            'summary': {
                'total_students': total_students,
                'registered': registered_count,
                'pending': pending_count,
                'registration_percentage': round(registration_percentage, 2)
            },
            'students': tracking_data
        })


class StudentRegistrationDetailView(APIView):
    """
    Admin API endpoint to view detailed registration information for a specific student.
    
    **Permissions**: Admin or Faculty
    
    **URL Parameters**:
    - student_id: ID of the student
    - registration_id: ID of the semester registration
    
    **Response**:
    Returns complete registration details including:
    - Student information
    - Academic details
    - Fee transactions (with UTR numbers)
    - Registered courses
    
    **Example**:
    GET /api/students/registration-detail/{student_id}/{registration_id}/
    """
    permission_classes = [IsAdminOrFaculty]
    
    def get(self, request, student_id, registration_id):
        try:
            # Fetch the student
            student = StudentProfile.objects.select_related(
                'user', 'program', 'department'
            ).get(id=student_id)
            
            # Fetch the registration
            registration = SemesterRegistration.objects.prefetch_related(
                'fee_transactions',
                'registered_courses__subject__course'
            ).get(id=registration_id, student=student)
            
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except SemesterRegistration.DoesNotExist:
            return Response(
                {'error': 'Registration not found for this student'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build detailed response
        response_data = {
            'student': {
                'id': student.id,
                'reg_no': student.reg_no or student.enrollment_number,
                'name': student.user.get_full_name() or student.user.username,
                'email': student.user.email,
                'phone': student.phone,
                'program': {
                    'name': student.program.name if student.program else 'N/A',
                    'code': student.program.code if student.program else 'N/A'
                },
                'department': {
                    'name': student.department.name if student.department else 'N/A',
                    'code': student.department.code if student.department else 'N/A'
                },
                'current_semester': student.current_semester,
                'batch_year': student.batch_year
            },
            'registration': {
                'id': registration.id,
                'academic_year': registration.academic_year,
                'semester': registration.semester,
                'institute_fee_paid': registration.institute_fee_paid,
                'hostel_fee_paid': registration.hostel_fee_paid,
                'hostel_room_no': registration.hostel_room_no,
                'total_credits': registration.total_credits,
                'approval_status': registration.approval_status,
                'approved_by_name': registration.approved_by.get_full_name() if registration.approved_by else None,
                'approved_at': registration.approved_at.isoformat() if registration.approved_at else None,
                'admin_notes': registration.admin_notes,
                'created_at': registration.created_at.isoformat(),
                'updated_at': registration.updated_at.isoformat()
            },
            'fee_transactions': [
                {
                    'id': txn.id,
                    'utr_no': txn.utr_no,
                    'bank_name': txn.bank_name,
                    'transaction_date': txn.transaction_date.isoformat(),
                    'amount': str(txn.amount),
                    'account_debited': txn.account_debited,
                    'account_credited': txn.account_credited,
                    'created_at': txn.created_at.isoformat()
                }
                for txn in registration.fee_transactions.all()
            ],
            'registered_courses': [
                {
                    'id': course.id,
                    'subject': {
                        'id': course.subject.id,
                        'name': course.subject.name,
                        'code': course.subject.code,
                        'credits': course.subject.credits,
                        'semester': course.subject.semester,
                        'course_name': course.subject.course.name if course.subject.course else 'N/A'
                    },
                    'is_backlog': course.is_backlog
                }
                for course in registration.registered_courses.all()
            ]
        }
        
        # Calculate totals
        total_fee_amount = sum(
            txn.amount for txn in registration.fee_transactions.all()
        )
        current_courses_count = sum(
            1 for c in registration.registered_courses.all() if not c.is_backlog
        )
        backlog_courses_count = sum(
            1 for c in registration.registered_courses.all() if c.is_backlog
        )
        
        response_data['summary'] = {
            'total_fee_transactions': registration.fee_transactions.count(),
            'total_fee_amount': str(total_fee_amount),
            'total_courses': registration.registered_courses.count(),
            'current_courses': current_courses_count,
            'backlog_courses': backlog_courses_count,
            'total_credits': registration.total_credits
        }
        
        return Response(response_data)


class ApproveRegistrationView(APIView):
    """
    Admin API endpoint to approve or reject a semester registration.
    
    **Permissions**: Admin only
    
    **POST Data**:
    - registration_id: ID of the semester registration
    - action: 'approve' or 'reject'
    - notes: Optional admin notes
    
    **On Approval**:
    - Updates registration status to 'approved'
    - Creates Enrollment records for all registered subjects
    - Updates student's current semester
    - Records admin and timestamp
    
    **On Rejection**:
    - Updates registration status to 'rejected'
    - Records admin notes and timestamp
    
    **Example**:
    POST /api/students/approve-registration/
    {
        "registration_id": 1,
        "action": "approve",
        "notes": "All documents verified"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Check if user is admin
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Admin privileges required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registration_id = request.data.get('registration_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        notes = request.data.get('notes', '')
        
        # Validate input
        if not registration_id:
            return Response(
                {'error': 'registration_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ['approve', 'reject']:
            return Response(
                {'error': 'action must be either "approve" or "reject".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the registration
        try:
            registration = SemesterRegistration.objects.select_related(
                'student', 'student__user'
            ).prefetch_related(
                'registered_courses__subject__course'
            ).get(id=registration_id)
        except SemesterRegistration.DoesNotExist:
            return Response(
                {'error': 'Registration not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already processed
        if registration.approval_status != 'pending':
            return Response(
                {'error': f'Registration has already been {registration.approval_status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Update registration status
                registration.approval_status = 'approved' if action == 'approve' else 'rejected'
                registration.approved_by = request.user
                registration.approved_at = timezone.now()
                registration.admin_notes = notes
                registration.save()
                
                # If approved, create enrollments and update student semester
                if action == 'approve':
                    student = registration.student
                    registered_courses = registration.registered_courses.all()
                    
                    # Extract semester number from registration
                    # Assuming semester format like "Jan-Jun 2026" or similar
                    # We'll increment the student's current semester
                    new_semester = student.current_semester + 1 if student.current_semester else 1
                    
                    # Create enrollment records for each registered subject
                    enrollments_created = []
                    for reg_course in registered_courses:
                        # Check if enrollment already exists
                        enrollment, created = Enrollment.objects.get_or_create(
                            student=student,
                            course=reg_course.subject.course,
                            semester=new_semester,
                            defaults={
                                'status': 'Active',
                                'date_enrolled': timezone.now().date()
                            }
                        )
                        
                        if created:
                            enrollments_created.append({
                                'subject': reg_course.subject.name,
                                'subject_code': reg_course.subject.code,
                                'credits': reg_course.subject.credits,
                                'is_backlog': reg_course.is_backlog
                            })
                    
                    # Update student's current semester
                    student.current_semester = new_semester
                    student.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Registration approved successfully.',
                        'registration': {
                            'id': registration.id,
                            'status': registration.approval_status,
                            'approved_by': request.user.get_full_name() or request.user.username,
                            'approved_at': registration.approved_at.isoformat(),
                            'notes': registration.admin_notes
                        },
                        'student': {
                            'id': student.id,
                            'name': student.user.get_full_name() or student.user.username,
                            'new_semester': new_semester
                        },
                        'enrollments_created': enrollments_created,
                        'total_enrollments': len(enrollments_created)
                    }, status=status.HTTP_200_OK)
                
                else:  # rejected
                    return Response({
                        'success': True,
                        'message': 'Registration rejected.',
                        'registration': {
                            'id': registration.id,
                            'status': registration.approval_status,
                            'approved_by': request.user.get_full_name() or request.user.username,
                            'approved_at': registration.approved_at.isoformat(),
                            'notes': registration.admin_notes
                        }
                    }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to process registration: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
