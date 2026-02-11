"""
Views for user profiles and dashboards.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import StudentProfile, FacultyProfile
from .serializers import StudentProfileSerializer, FacultyProfileSerializer


class IsStudent(IsAuthenticated):
    """
    Custom permission to only allow students to access the view.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        # Then check if user has STUDENT role
        return request.user.role == 'STUDENT'


class IsFaculty(IsAuthenticated):
    """
    Custom permission to only allow faculty to access the view.
    """
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        # Then check if user has FACULTY role
        return request.user.role == 'FACULTY'


class StudentDashboardView(APIView):
    """
    API endpoint for student dashboard.
    Retrieves the logged-in student's profile information.
    
    Permissions: IsAuthenticated AND User role is STUDENT
    """
    permission_classes = [IsStudent]
    
    def get(self, request):
        """
        Get the current student's profile.
        """
        try:
            student_profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    'error': 'Student profile not found',
                    'detail': 'No student profile exists for this user. Please contact administration.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentProfileSerializer(student_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        """
        Update the current student's profile (partial update).
        """
        try:
            student_profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response(
                {
                    'error': 'Student profile not found',
                    'detail': 'No student profile exists for this user.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentProfileSerializer(
            student_profile,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyDashboardView(APIView):
    """
    API endpoint for faculty dashboard.
    Retrieves the logged-in faculty member's profile information.
    
    Permissions: IsAuthenticated AND User role is FACULTY
    """
    permission_classes = [IsFaculty]
    
    def get(self, request):
        """
        Get the current faculty member's profile.
        """
        try:
            faculty_profile = request.user.faculty_profile
        except FacultyProfile.DoesNotExist:
            return Response(
                {
                    'error': 'Faculty profile not found',
                    'detail': 'No faculty profile exists for this user. Please contact administration.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FacultyProfileSerializer(faculty_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        """
        Update the current faculty member's profile (partial update).
        """
        try:
            faculty_profile = request.user.faculty_profile
        except FacultyProfile.DoesNotExist:
            return Response(
                {
                    'error': 'Faculty profile not found',
                    'detail': 'No faculty profile exists for this user.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FacultyProfileSerializer(
            faculty_profile,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
