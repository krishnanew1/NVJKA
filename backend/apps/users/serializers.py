"""
Serializers for user profiles and authentication.
"""
from rest_framework import serializers
from .models import CustomUser, StudentProfile, FacultyProfile
from apps.academics.models import Department


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
    Serializer for StudentProfile with nested user data and custom_data support.
    
    Multi-tenant support: Handles custom_data JSONField for institution-specific fields.
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
    
    # Program support
    program = serializers.SerializerMethodField()
    program_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Custom data field for dynamic registration fields
    custom_data = serializers.JSONField(required=False, default=dict)
    
    # Alias for enrollment_number (commonly referred to as roll_number)
    roll_number = serializers.CharField(read_only=True, source='enrollment_number')
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'reg_no',
            'enrollment_number',
            'roll_number',
            'dob',
            'gender',
            'phone',
            'address',
            'program',
            'program_id',
            'department',
            'department_id',
            'current_semester',
            'batch_year',
            'custom_data',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_program(self, obj):
        """Get program information if assigned."""
        if obj.program:
            return {
                'id': obj.program.id,
                'name': obj.program.name,
                'code': obj.program.code,
                'duration_years': obj.program.duration_years,
                'duration_semesters': obj.program.duration_semesters
            }
        return None
    
    def validate_reg_no(self, value):
        """Ensure registration number is unique."""
        instance = self.instance
        if StudentProfile.objects.filter(reg_no=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("This registration number is already in use.")
        return value
    
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
    
    def validate_program_id(self, value):
        """Validate that the program exists."""
        if value is not None:
            from apps.academics.models import Program
            try:
                Program.objects.get(id=value)
            except Program.DoesNotExist:
                raise serializers.ValidationError("Program with this ID does not exist.")
        return value
    
    def validate_custom_data(self, value):
        """Validate custom_data is a valid JSON object."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("custom_data must be a JSON object.")
        return value
    
    def create(self, validated_data):
        """Create student profile with program and custom_data."""
        program_id = validated_data.pop('program_id', None)
        
        if program_id:
            from apps.academics.models import Program
            program = Program.objects.get(id=program_id)
            validated_data['program'] = program
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update student profile with optional program change."""
        if 'program_id' in validated_data:
            program_id = validated_data.pop('program_id')
            if program_id:
                from apps.academics.models import Program
                program = Program.objects.get(id=program_id)
                validated_data['program'] = program
            else:
                validated_data['program'] = None
        
        return super().update(instance, validated_data)


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
