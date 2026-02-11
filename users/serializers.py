"""
Serializers for user profiles and authentication.
"""
from rest_framework import serializers
from .models import CustomUser, StudentProfile, FacultyProfile
from academics.models import Department


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user information serializer for nested serialization.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone_number']
        read_only_fields = ['id', 'username', 'role']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class DepartmentBasicSerializer(serializers.ModelSerializer):
    """
    Basic department information for nested serialization.
    """
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description']
        read_only_fields = ['id']


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentProfile with nested user data.
    """
    user = UserBasicSerializer(read_only=True)
    department = DepartmentBasicSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'enrollment_number',
            'department',
            'department_id',
            'current_semester',
            'batch_year',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_enrollment_number(self, value):
        """Ensure enrollment number is unique."""
        instance = self.instance
        if StudentProfile.objects.filter(enrollment_number=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("This enrollment number is already in use.")
        return value
    
    def validate_current_semester(self, value):
        """Ensure semester is positive."""
        if value < 1:
            raise serializers.ValidationError("Semester must be at least 1.")
        return value


class FacultyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for FacultyProfile with nested user data.
    """
    user = UserBasicSerializer(read_only=True)
    department = DepartmentBasicSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = FacultyProfile
        fields = [
            'id',
            'user',
            'employee_id',
            'department',
            'department_id',
            'designation',
            'specialization',
            'date_of_joining',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_employee_id(self, value):
        """Ensure employee ID is unique."""
        instance = self.instance
        if FacultyProfile.objects.filter(employee_id=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("This employee ID is already in use.")
        return value
