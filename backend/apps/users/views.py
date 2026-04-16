"""
Views for user profiles and dashboards.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import CustomUser, StudentProfile, FacultyProfile
from .serializers import StudentProfileSerializer, FacultyProfileSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user role and profile information.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token
        token['role'] = user.role
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that uses our custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer


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



class RegisterUserView(APIView):
    """
    API endpoint for user registration with profile creation.
    Supports dynamic custom_data for multi-tenant architecture.
    
    Permissions: AllowAny (public registration) or IsAuthenticated (admin creating users)
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] if only admins can register users
    
    @transaction.atomic
    def post(self, request):
        """
        Register a new user with profile.
        
        Expected payload:
        {
            "user": {
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePass123",
                "role": "STUDENT"  # or "FACULTY"
            },
            "profile": {
                "reg_no": "2026CS001",  # for students
                "enrollment_number": "2026CS001",  # for students
                "employee_id": "EMP001",  # for faculty
                "dob": "2005-05-15",
                "gender": "M",
                "phone": "+91-9876543210",
                "address": "123 Main St",
                "program_id": 1,  # for students
                "department_id": 1,
                "current_semester": 1,  # for students
                "batch_year": 2026,  # for students
                "designation": "Professor",  # for faculty
                "specialization": "AI/ML",  # for faculty
                "date_of_joining": "2020-01-01",  # for faculty
                "custom_data": {  # for students (multi-tenant)
                    "aadhar_number": "1234-5678-9012",
                    "samagra_id": "ABC123456"
                }
            }
        }
        """
        user_data = request.data.get('user', {})
        profile_data = request.data.get('profile', {})
        
        # Validate required user fields
        required_user_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_user_fields if not user_data.get(field)]
        if missing_fields:
            return Response(
                {
                    'error': 'Missing required fields',
                    'detail': f'The following fields are required: {", ".join(missing_fields)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get role (default to STUDENT if not provided)
        role = user_data.get('role', 'STUDENT').upper()
        if role not in ['STUDENT', 'FACULTY', 'ADMIN']:
            return Response(
                {
                    'error': 'Invalid role',
                    'detail': 'Role must be one of: STUDENT, FACULTY, ADMIN'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username already exists
        if CustomUser.objects.filter(username=user_data['username']).exists():
            return Response(
                {
                    'error': 'Username already exists',
                    'detail': 'A user with this username already exists.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email already exists
        if CustomUser.objects.filter(email=user_data['email']).exists():
            return Response(
                {
                    'error': 'Email already exists',
                    'detail': 'A user with this email already exists.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role=role
            )
            
            # Create profile based on role
            if role == 'STUDENT':
                # Validate required student fields
                if not profile_data.get('reg_no'):
                    user.delete()
                    return Response(
                        {
                            'error': 'Missing required field',
                            'detail': 'reg_no is required for student registration'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Set enrollment_number to reg_no if not provided
                if not profile_data.get('enrollment_number'):
                    profile_data['enrollment_number'] = profile_data['reg_no']
                
                # Check if profile was auto-created by signal
                try:
                    profile = StudentProfile.objects.get(user=user)
                    # Update existing profile
                    serializer = StudentProfileSerializer(profile, data=profile_data, partial=True)
                except StudentProfile.DoesNotExist:
                    # Create new profile
                    serializer = StudentProfileSerializer(data=profile_data)
                
                if serializer.is_valid():
                    profile = serializer.save(user=user)
                    return Response(
                        {
                            'message': 'Student registered successfully',
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'role': user.role
                            },
                            'profile': serializer.data
                        },
                        status=status.HTTP_201_CREATED
                    )
                else:
                    user.delete()
                    return Response(
                        {
                            'error': 'Profile validation failed',
                            'detail': serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            elif role == 'FACULTY':
                # Validate required faculty fields
                required_faculty_fields = ['employee_id', 'department_id']
                missing_fields = [field for field in required_faculty_fields if not profile_data.get(field)]
                if missing_fields:
                    user.delete()
                    return Response(
                        {
                            'error': 'Missing required fields',
                            'detail': f'The following fields are required for faculty: {", ".join(missing_fields)}'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create faculty profile
                serializer = FacultyProfileSerializer(data=profile_data)
                
                if serializer.is_valid():
                    profile = serializer.save(user=user)
                    return Response(
                        {
                            'message': 'Faculty registered successfully',
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'role': user.role
                            },
                            'profile': serializer.data
                        },
                        status=status.HTTP_201_CREATED
                    )
                else:
                    user.delete()
                    return Response(
                        {
                            'error': 'Profile validation failed',
                            'detail': serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            else:  # ADMIN
                # Admin users don't need a profile
                return Response(
                    {
                        'message': 'Admin user registered successfully',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'role': user.role
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            return Response(
                {
                    'error': 'Registration failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentListView(APIView):
    """
    API endpoint to list all students.
    
    Permissions: IsAuthenticated
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get list of all students with their profiles.
        Always returns 200 OK with empty array if no students exist.
        """
        try:
            students = StudentProfile.objects.select_related(
                'user', 'department', 'program'
            ).all().order_by('-created_at')
            
            serializer = StudentProfileSerializer(students, many=True)
            
            return Response(
                {
                    'count': students.count(),
                    'results': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the error but return empty list to prevent frontend errors
            print(f"Error fetching students: {str(e)}")
            return Response(
                {
                    'count': 0,
                    'results': [],
                    'error': 'Failed to fetch students'
                },
                status=status.HTTP_200_OK  # Still return 200 to prevent frontend error state
            )
