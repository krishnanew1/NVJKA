"""
Views for academics app.

This module provides REST API viewsets for Department, Course, and Subject
models with authentication, filtering, and search capabilities.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Course, Subject, Timetable
from .serializers import (
    DepartmentSerializer, DepartmentDetailSerializer,
    CourseSerializer, CourseDetailSerializer,
    SubjectSerializer, TimetableSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.
    
    Provides CRUD operations for departments with authentication,
    filtering, and search capabilities.
    """
    
    queryset = Department.objects.all().order_by('code')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    
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
    """
    
    queryset = Course.objects.select_related('department').all().order_by('department__code', 'code')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
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
    
    queryset = Subject.objects.select_related('course__department').all().order_by('course__code', 'semester', 'code')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'name', 'code', 'course', 'course__name', 'course__code', 
        'course__department', 'course__department__name', 'course__department__code',
        'semester', 'credits', 'is_mandatory'
    ]
    search_fields = [
        'name', 'code', 'description', 
        'course__name', 'course__code',
        'course__department__name', 'course__department__code'
    ]
    ordering_fields = [
        'name', 'code', 'course__code', 'semester', 'credits', 
        'is_mandatory', 'created_at'
    ]
    ordering = ['course__code', 'semester', 'code']


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Timetable model.
    
    Provides CRUD operations for timetable entries with nested subject,
    course, and department information, authentication, filtering, and search.
    """
    
    queryset = Timetable.objects.select_related(
        'subject__course__department'
    ).all().order_by('day_of_week', 'start_time', 'class_name')
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'class_name', 'subject', 'subject__name', 'subject__code',
        'subject__course', 'subject__course__name', 'subject__course__code',
        'subject__course__department', 'subject__course__department__name', 'subject__course__department__code',
        'day_of_week', 'room_number', 'academic_year', 'is_active'
    ]
    search_fields = [
        'class_name', 'room_number', 'academic_year',
        'subject__name', 'subject__code',
        'subject__course__name', 'subject__course__code',
        'subject__course__department__name', 'subject__course__department__code'
    ]
    ordering_fields = [
        'class_name', 'day_of_week', 'start_time', 'end_time',
        'academic_year', 'is_active', 'created_at'
    ]
    ordering = ['day_of_week', 'start_time', 'class_name']
