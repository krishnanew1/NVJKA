"""
Views for academics app.

This module provides REST API viewsets for Department, Course, Subject,
CustomRegistrationField, and Program models with authentication, filtering, and search capabilities.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import Department, Course, Subject, Timetable, CustomRegistrationField, Program
from .serializers import (
    DepartmentSerializer, DepartmentDetailSerializer,
    CourseSerializer, CourseDetailSerializer,
    SubjectSerializer, TimetableSerializer,
    CustomRegistrationFieldSerializer, ProgramSerializer
)
from .utils import generate_batch_timetable, get_batch_timetable


class CustomRegistrationFieldViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CustomRegistrationField model.
    
    Allows institutions to dynamically configure registration fields
    without code changes. Only active fields are returned by default.
    """
    
    queryset = CustomRegistrationField.objects.all().order_by('order', 'field_name')
    serializer_class = CustomRegistrationFieldSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field_type', 'is_required', 'is_active']
    search_fields = ['field_name', 'field_label', 'help_text']
    ordering_fields = ['order', 'field_name', 'created_at']
    ordering = ['order', 'field_name']
    
    def get_queryset(self):
        """
        Return queryset filtered by active status.
        
        By default, only active fields are returned unless
        'show_inactive=true' is passed as a query parameter.
        """
        queryset = super().get_queryset()
        
        # Filter by active status unless explicitly requested
        show_inactive = self.request.query_params.get('show_inactive', 'false').lower() == 'true'
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active_fields(self, request):
        """
        Get all active registration fields ordered by display order.
        
        This endpoint is used by the registration form to dynamically
        render custom fields.
        """
        fields = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(fields, many=True)
        return Response(serializer.data)


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Program model.
    
    Provides CRUD operations for academic programs with authentication,
    filtering, and search capabilities.
    """
    
    queryset = Program.objects.all().select_related('department').order_by('department__code', 'code')
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'duration_years', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'duration_years', 'created_at']
    ordering = ['department__code', 'code']
    
    def get_queryset(self):
        """
        Return queryset filtered by active status.
        
        By default, only active programs are returned unless
        'show_inactive=true' is passed as a query parameter.
        """
        queryset = super().get_queryset()
        
        # Filter by active status unless explicitly requested
        show_inactive = self.request.query_params.get('show_inactive', 'false').lower() == 'true'
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """
        Get programs grouped by department.
        
        Returns a dictionary with department codes as keys and
        lists of programs as values.
        """
        department_code = request.query_params.get('department')
        
        if department_code:
            programs = self.get_queryset().filter(department__code=department_code)
        else:
            programs = self.get_queryset()
        
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.
    
    Provides CRUD operations for departments with authentication,
    filtering, and search capabilities.
    
    Permissions:
    - List/Retrieve: Any authenticated user
    - Create/Update/Delete: Admin only
    """
    
    queryset = Department.objects.all().order_by('code')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow only admins to create, update, or delete departments.
        """
        from apps.common.permissions import IsAdminUser
        
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Uses detailed serializer for retrieve action to include
        nested course information.
        """
        if self.action == 'retrieve':
            return DepartmentDetailSerializer
        return DepartmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model.
    
    Provides CRUD operations for courses with nested department information,
    authentication, filtering, and search capabilities.
    
    Permissions:
    - List/Retrieve: Any authenticated user
    - Create/Update/Delete: Admin only
    """
    
    queryset = Course.objects.select_related('department').all().order_by('department__code', 'code')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow only admins to create, update, or delete courses.
        """
        from apps.common.permissions import IsAdminUser
        
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'code', 'department', 'department__name', 'department__code', 'credits', 'duration_years']
    search_fields = ['name', 'code', 'description', 'department__name', 'department__code']
    ordering_fields = ['name', 'code', 'department__code', 'credits', 'duration_years', 'created_at']
    ordering = ['department__code', 'code']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        
        Uses detailed serializer for retrieve action to include
        nested subject information.
        """
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject model.
    
    Provides CRUD operations for subjects with nested course and department
    information, authentication, filtering, and search capabilities.
    """
    
    queryset = Subject.objects.select_related('course__department', 'faculty__user').all().order_by('course__code', 'semester', 'code')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'name', 'code', 'course', 'course__name', 'course__code', 
        'course__department', 'course__department__name', 'course__department__code',
        'semester', 'credits', 'is_mandatory', 'faculty'
    ]
    search_fields = [
        'name', 'code', 'description', 
        'course__name', 'course__code',
        'course__department__name', 'course__department__code',
        'faculty__user__first_name', 'faculty__user__last_name', 'faculty__employee_id'
    ]
    ordering_fields = [
        'name', 'code', 'course__code', 'semester', 'credits', 
        'is_mandatory', 'created_at'
    ]
    ordering = ['course__code', 'semester', 'code']
    
    @action(detail=True, methods=['patch', 'put'], url_path='assign-faculty')
    def assign_faculty(self, request, pk=None):
        """
        Assign a faculty member to a subject.
        
        PATCH/PUT /api/academics/subjects/{id}/assign-faculty/
        
        Request Body:
        {
            "faculty_id": 5  // ID of the FacultyProfile to assign (null to unassign)
        }
        
        Returns:
        {
            "success": true,
            "message": "Faculty assigned successfully",
            "data": {
                "id": 1,
                "name": "Operating Systems",
                "code": "CS301",
                "faculty": {
                    "id": 5,
                    "employee_id": "FAC102",
                    "name": "Deepak Kumar Dewangan",
                    "designation": "Assistant Professor"
                }
            }
        }
        """
        from apps.users.models import FacultyProfile
        
        subject = self.get_object()
        faculty_id = request.data.get('faculty_id')
        
        # Allow null to unassign faculty
        if faculty_id is None:
            subject.faculty = None
            subject.save()
            
            return Response({
                'success': True,
                'message': 'Faculty unassigned successfully',
                'data': self.get_serializer(subject).data
            }, status=status.HTTP_200_OK)
        
        # Validate faculty_id
        try:
            faculty_id = int(faculty_id)
            faculty = FacultyProfile.objects.select_related('user', 'department').get(id=faculty_id)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'faculty_id must be a valid integer',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except FacultyProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Faculty with ID {faculty_id} not found',
                'code': 404
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Assign faculty to subject
        subject.faculty = faculty
        subject.save()
        
        return Response({
            'success': True,
            'message': f'Faculty {faculty.user.get_full_name()} assigned to {subject.name}',
            'data': self.get_serializer(subject).data
        }, status=status.HTTP_200_OK)


class MySubjectsView(ListAPIView):
    """
    View to list subjects assigned to the currently logged-in faculty member.
    
    GET /api/faculty/my-subjects/
    
    Returns all subjects where the faculty field matches the current user's FacultyProfile.
    Requires authentication and that the user has a FacultyProfile.
    
    Returns:
    [
        {
            "id": 1,
            "name": "Operating Systems",
            "code": "CS301",
            "course": {...},
            "semester": 3,
            "semester_display": "Semester 3",
            "credits": 4,
            "is_mandatory": true,
            "faculty_info": {...}
        },
        ...
    ]
    """
    
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter subjects by the currently logged-in faculty member.
        
        Returns subjects where faculty.user matches request.user.
        """
        from apps.users.models import FacultyProfile
        
        # Get the faculty profile for the current user
        try:
            faculty_profile = FacultyProfile.objects.get(user=self.request.user)
        except FacultyProfile.DoesNotExist:
            # If user doesn't have a faculty profile, return empty queryset
            return Subject.objects.none()
        
        # Return subjects assigned to this faculty member
        return Subject.objects.select_related(
            'course__department', 'faculty__user'
        ).filter(
            faculty=faculty_profile
        ).order_by('course__code', 'semester', 'code')


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Timetable model.
    
    Provides CRUD operations for timetable entries with nested subject,
    course, and department information, authentication, filtering, and search.
    
    Custom Filters:
    - student_id: Filter timetable by student's enrolled courses
    - faculty_id: Filter timetable by faculty assignments
    - day_of_week: Filter by specific day
    
    Custom Actions:
    - generate: Auto-generate timetable for a batch
    """
    
    queryset = Timetable.objects.select_related(
        'subject__course__department', 'faculty__user'
    ).all().order_by('day_of_week', 'start_time', 'class_name')
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'class_name', 'subject', 'subject__name', 'subject__code',
        'subject__course', 'subject__course__name', 'subject__course__code',
        'subject__course__department', 'subject__course__department__name', 'subject__course__department__code',
        'day_of_week', 'room_number', 'classroom', 'academic_year', 'is_active', 'faculty'
    ]
    search_fields = [
        'class_name', 'room_number', 'classroom', 'academic_year',
        'subject__name', 'subject__code',
        'subject__course__name', 'subject__course__code',
        'subject__course__department__name', 'subject__course__department__code',
        'faculty__user__first_name', 'faculty__user__last_name', 'faculty__employee_id'
    ]
    ordering_fields = [
        'class_name', 'day_of_week', 'start_time', 'end_time',
        'academic_year', 'is_active', 'created_at'
    ]
    ordering = ['day_of_week', 'start_time', 'class_name']

    def get_queryset(self):
        """
        Optionally filter timetable by student_id, faculty_id, or day_of_week.
        
        Query Parameters:
        - student_id: Returns timetable for courses the student is enrolled in
        - faculty_id: Returns timetable for classes assigned to this faculty
        - day_of_week: Returns timetable for a specific day (MONDAY, TUESDAY, etc.)
        """
        queryset = super().get_queryset()
        
        # Filter by student_id
        student_id = self.request.query_params.get('student_id')
        if student_id:
            # Get all courses the student is enrolled in
            from apps.students.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                student_id=student_id,
                status='Active'
            ).values_list('course_id', flat=True)
            
            # Filter timetable by subjects in those courses
            queryset = queryset.filter(subject__course_id__in=enrolled_courses)
        
        # Filter by faculty_id
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)
        
        # Filter by day_of_week (already handled by filterset_fields, but can be explicit)
        day_of_week = self.request.query_params.get('day_of_week')
        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week.upper())
        
        return queryset

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_timetable(self, request):
        """
        Auto-generate timetable for a specific batch.
        
        POST /api/academics/timetable/generate/
        
        Request Body:
        {
            "batch_year": 2024,
            "department_id": 1,  // optional
            "semester": 3,       // optional
            "academic_year": "2026-27"  // optional
        }
        
        Returns:
        {
            "success": true,
            "message": "Timetable generated successfully",
            "data": {
                "batch_year": 2024,
                "semester": 3,
                "class_name": "CSE-2024-S3",
                "academic_year": "2026-27",
                "total_subjects": 6,
                "scheduled_subjects": 5,
                "failed_subjects": 1,
                "total_entries": 20,
                "generated_entries": [...],
                "failed_subjects_details": [...]
            }
        }
        """
        # Extract parameters from request
        batch_year = request.data.get('batch_year')
        department_id = request.data.get('department_id')
        semester = request.data.get('semester')
        academic_year = request.data.get('academic_year')
        
        # Validate required parameters
        if not batch_year:
            return Response({
                'success': False,
                'error': 'batch_year is required',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            batch_year = int(batch_year)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'batch_year must be a valid integer',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate optional parameters
        if department_id:
            try:
                department_id = int(department_id)
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'department_id must be a valid integer',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if semester:
            try:
                semester = int(semester)
                if semester < 1 or semester > 8:
                    raise ValueError("Semester must be between 1 and 8")
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'semester must be a valid integer between 1 and 8',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate timetable
            result = generate_batch_timetable(
                batch_year=batch_year,
                department_id=department_id,
                semester=semester,
                academic_year=academic_year
            )
            
            return Response({
                'success': True,
                'message': f'Timetable generated successfully for batch {batch_year}',
                'data': result
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'error': str(e),
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to generate timetable: {str(e)}',
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='batch')
    def get_batch_timetable(self, request):
        """
        Retrieve timetable for a specific batch.
        
        GET /api/academics/timetable/batch/?batch_year=2024&department_id=1&semester=3
        
        Query Parameters:
        - batch_year: Required - Year of admission
        - department_id: Optional - Department filter
        - semester: Optional - Semester filter
        - academic_year: Optional - Academic year
        
        Returns:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "class_name": "CSE-2024-S3",
                    "subject": {...},
                    "faculty": {...},
                    "day_of_week": "MONDAY",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "classroom": "Room-101",
                    "academic_year": "2026-27"
                },
                ...
            ]
        }
        """
        # Extract parameters from query params
        batch_year = request.query_params.get('batch_year')
        department_id = request.query_params.get('department_id')
        semester = request.query_params.get('semester')
        academic_year = request.query_params.get('academic_year')
        
        # Validate required parameters
        if not batch_year:
            return Response({
                'success': False,
                'error': 'batch_year query parameter is required',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            batch_year = int(batch_year)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'batch_year must be a valid integer',
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate optional parameters
        if department_id:
            try:
                department_id = int(department_id)
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'department_id must be a valid integer',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if semester:
            try:
                semester = int(semester)
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'semester must be a valid integer',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get batch timetable
            timetable_entries = get_batch_timetable(
                batch_year=batch_year,
                department_id=department_id,
                semester=semester,
                academic_year=academic_year
            )
            
            return Response({
                'success': True,
                'data': timetable_entries
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to retrieve timetable: {str(e)}',
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
