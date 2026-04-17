"""
Serializers for academics app models.

This module provides Django REST Framework serializers for Department, Course,
Subject, Timetable, CustomRegistrationField, and Program models with nested serialization support.
"""

from rest_framework import serializers
from .models import Department, Course, Subject, Timetable, CustomRegistrationField, Program


class CustomRegistrationFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomRegistrationField model.
    
    Allows institutions to dynamically configure registration fields
    without code changes.
    """
    
    dropdown_options_list = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomRegistrationField
        fields = [
            'id',
            'field_name',
            'field_label',
            'field_type',
            'dropdown_options',
            'dropdown_options_list',
            'is_required',
            'placeholder',
            'help_text',
            'order',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_dropdown_options_list(self, obj):
        """Convert comma-separated dropdown options to a list."""
        if obj.field_type == 'dropdown' and obj.dropdown_options:
            return [opt.strip() for opt in obj.dropdown_options.split(',') if opt.strip()]
        return []
    
    def validate(self, data):
        """Validate that dropdown fields have options."""
        if data.get('field_type') == 'dropdown':
            if not data.get('dropdown_options'):
                raise serializers.ValidationError({
                    'dropdown_options': 'Dropdown fields must have options specified.'
                })
        return data


class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for Program model.
    
    Represents academic programs (e.g., B.Tech, M.Sc) that can be
    dynamically configured by institutions.
    """
    
    # Nested department information
    department = serializers.SerializerMethodField()
    
    # Write-only field for creating/updating programs
    department_id = serializers.IntegerField(write_only=True)
    
    # Read-only computed fields
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = [
            'id',
            'name',
            'code',
            'department',
            'department_id',
            'duration_years',
            'duration_semesters',
            'total_credits',
            'description',
            'is_active',
            'total_students',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_students']
    
    def get_department(self, obj):
        """Get basic department information."""
        if obj.department:
            return {
                'id': obj.department.id,
                'name': obj.department.name,
                'code': obj.department.code
            }
        return None
    
    def get_total_students(self, obj):
        """Get the total number of students enrolled in this program."""
        return obj.students.count()
    
    def validate_department_id(self, value):
        """Validate that the department exists."""
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Department with this ID does not exist.")
        return value
    
    def validate(self, data):
        """Validate program data."""
        # Auto-calculate semesters from years if not provided
        if 'duration_years' in data and 'duration_semesters' not in data:
            data['duration_semesters'] = data['duration_years'] * 2
        return data
    
    def create(self, validated_data):
        """Create a new program with the specified department."""
        department_id = validated_data.pop('department_id')
        department = Department.objects.get(id=department_id)
        validated_data['department'] = department
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update program with optional department change."""
        if 'department_id' in validated_data:
            department_id = validated_data.pop('department_id')
            department = Department.objects.get(id=department_id)
            validated_data['department'] = department
        return super().update(instance, validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    
    Provides basic serialization for department data including
    computed fields for additional information.
    """
    
    # Read-only computed fields
    total_courses = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'description',
            'total_courses',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_courses']
    
    def get_total_courses(self, obj):
        """Get the total number of courses in this department."""
        return obj.courses.count()


class DepartmentDetailSerializer(DepartmentSerializer):
    """
    Detailed serializer for Department model.
    
    Includes nested course information for detailed department views.
    """
    
    courses = serializers.SerializerMethodField()
    
    class Meta(DepartmentSerializer.Meta):
        fields = DepartmentSerializer.Meta.fields + ['courses']
    
    def get_courses(self, obj):
        """Get basic course information for this department."""
        courses = obj.courses.all()
        return [
            {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'credits': course.credits,
                'duration_years': course.duration_years
            }
            for course in courses
        ]


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model with nested Department information.
    
    Shows complete department details within course data for
    comprehensive course information display.
    """
    
    # Nested department serialization
    department = DepartmentSerializer(read_only=True)
    
    # Write-only field for creating/updating courses
    department_id = serializers.IntegerField(write_only=True)
    
    # Read-only computed fields
    total_subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'code',
            'department',
            'department_id',
            'credits',
            'duration_years',
            'description',
            'total_subjects',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_subjects']
    
    def get_total_subjects(self, obj):
        """Get the total number of subjects in this course."""
        return obj.subjects.count()
    
    def validate_department_id(self, value):
        """Validate that the department exists."""
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Department with this ID does not exist.")
        return value
    
    def create(self, validated_data):
        """Create a new course with the specified department."""
        department_id = validated_data.pop('department_id')
        department = Department.objects.get(id=department_id)
        validated_data['department'] = department
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update course with optional department change."""
        if 'department_id' in validated_data:
            department_id = validated_data.pop('department_id')
            department = Department.objects.get(id=department_id)
            validated_data['department'] = department
        return super().update(instance, validated_data)


class CourseDetailSerializer(CourseSerializer):
    """
    Detailed serializer for Course model.
    
    Includes nested subject information for detailed course views.
    """
    
    subjects = serializers.SerializerMethodField()
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['subjects']
    
    def get_subjects(self, obj):
        """Get basic subject information for this course."""
        subjects = obj.subjects.all().order_by('semester', 'code')
        return [
            {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'semester': subject.semester,
                'credits': subject.credits,
                'is_mandatory': subject.is_mandatory
            }
            for subject in subjects
        ]


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Subject model with nested Course and Department information.
    
    Provides comprehensive subject information including related course
    and department details, plus faculty assignment information.
    """
    
    # Nested course serialization (which includes department)
    course = CourseSerializer(read_only=True)
    
    # Write-only field for creating/updating subjects
    course_id = serializers.IntegerField(write_only=True)
    
    # Faculty information
    faculty_info = serializers.SerializerMethodField()
    faculty_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Read-only computed fields
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    total_timetable_entries = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'code',
            'course',
            'course_id',
            'faculty_info',
            'faculty_id',
            'semester',
            'semester_display',
            'credits',
            'is_mandatory',
            'description',
            'total_timetable_entries',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_timetable_entries']
    
    def get_faculty_info(self, obj):
        """Get faculty information if assigned."""
        if obj.faculty:
            return {
                'id': obj.faculty.id,
                'employee_id': obj.faculty.employee_id,
                'name': obj.faculty.user.get_full_name() or obj.faculty.user.username,
                'designation': obj.faculty.designation,
            }
        return None
    
    def get_total_timetable_entries(self, obj):
        """Get the total number of timetable entries for this subject."""
        return obj.timetable_entries.count()
    
    def validate_course_id(self, value):
        """Validate that the course exists."""
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course with this ID does not exist.")
        return value
    
    def validate_faculty_id(self, value):
        """Validate that the faculty exists."""
        if value is not None:
            from apps.users.models import FacultyProfile
            try:
                FacultyProfile.objects.get(id=value)
            except FacultyProfile.DoesNotExist:
                raise serializers.ValidationError("Faculty with this ID does not exist.")
        return value
    
    def validate(self, data):
        """Validate subject data including unique constraints."""
        # Check unique_together constraint for code and course
        if 'course_id' in data and 'code' in data:
            course_id = data['course_id']
            code = data['code']
            
            # For updates, exclude the current instance
            queryset = Subject.objects.filter(course_id=course_id, code=code)
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'code': 'Subject with this code already exists in the selected course.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create a new subject with the specified course and faculty."""
        course_id = validated_data.pop('course_id')
        faculty_id = validated_data.pop('faculty_id', None)
        
        course = Course.objects.get(id=course_id)
        validated_data['course'] = course
        
        if faculty_id:
            from apps.users.models import FacultyProfile
            faculty = FacultyProfile.objects.get(id=faculty_id)
            validated_data['faculty'] = faculty
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update subject with optional course and faculty change."""
        if 'course_id' in validated_data:
            course_id = validated_data.pop('course_id')
            course = Course.objects.get(id=course_id)
            validated_data['course'] = course
        
        if 'faculty_id' in validated_data:
            faculty_id = validated_data.pop('faculty_id')
            if faculty_id:
                from apps.users.models import FacultyProfile
                faculty = FacultyProfile.objects.get(id=faculty_id)
                validated_data['faculty'] = faculty
            else:
                validated_data['faculty'] = None
        
        return super().update(instance, validated_data)


class TimetableSerializer(serializers.ModelSerializer):
    """
    Serializer for Timetable model with nested Subject and Faculty information.
    
    Provides comprehensive timetable information including related subject,
    course, department, and faculty details through nested serialization.
    """
    
    # Nested subject serialization (which includes course and department)
    subject = SubjectSerializer(read_only=True)
    
    # Nested faculty information
    faculty_info = serializers.SerializerMethodField()
    
    # Write-only fields for creating/updating timetable entries
    subject_id = serializers.IntegerField(write_only=True)
    faculty_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Read-only computed fields
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = [
            'id',
            'class_name',
            'subject',
            'subject_id',
            'faculty_info',
            'faculty_id',
            'day_of_week',
            'day_display',
            'start_time',
            'end_time',
            'duration_minutes',
            'room_number',
            'classroom',
            'academic_year',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'duration_minutes']
    
    def get_faculty_info(self, obj):
        """Get faculty information if assigned."""
        if obj.faculty:
            return {
                'id': obj.faculty.id,
                'employee_id': obj.faculty.employee_id,
                'name': obj.faculty.user.get_full_name() or obj.faculty.user.username,
                'designation': obj.faculty.designation,
            }
        return None
    
    def get_duration_minutes(self, obj):
        """Calculate the duration of the class in minutes."""
        if obj.start_time and obj.end_time:
            start_minutes = obj.start_time.hour * 60 + obj.start_time.minute
            end_minutes = obj.end_time.hour * 60 + obj.end_time.minute
            return end_minutes - start_minutes
        return None
    
    def validate_subject_id(self, value):
        """Validate that the subject exists."""
        try:
            Subject.objects.get(id=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject with this ID does not exist.")
        return value
    
    def validate_faculty_id(self, value):
        """Validate that the faculty exists."""
        if value is not None:
            from apps.users.models import FacultyProfile
            try:
                FacultyProfile.objects.get(id=value)
            except FacultyProfile.DoesNotExist:
                raise serializers.ValidationError("Faculty with this ID does not exist.")
        return value
    
    def validate(self, data):
        """Validate timetable data including time constraints and unique constraints."""
        # Validate time constraints
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        
        # Check unique constraints
        if all(key in data for key in ['class_name', 'day_of_week', 'start_time', 'academic_year']):
            queryset = Timetable.objects.filter(
                class_name=data['class_name'],
                day_of_week=data['day_of_week'],
                start_time=data['start_time'],
                academic_year=data['academic_year']
            )
            
            # For updates, exclude the current instance
            if self.instance:
                queryset = queryset.exclude(id=self.instance.id)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'non_field_errors': [
                        'A timetable entry already exists for this class, day, time, and academic year.'
                    ]
                })
        
        return data
    
    def create(self, validated_data):
        """Create a new timetable entry with the specified subject and faculty."""
        subject_id = validated_data.pop('subject_id')
        faculty_id = validated_data.pop('faculty_id', None)
        
        subject = Subject.objects.get(id=subject_id)
        validated_data['subject'] = subject
        
        if faculty_id:
            from apps.users.models import FacultyProfile
            faculty = FacultyProfile.objects.get(id=faculty_id)
            validated_data['faculty'] = faculty
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update timetable entry with optional subject and faculty change."""
        if 'subject_id' in validated_data:
            subject_id = validated_data.pop('subject_id')
            subject = Subject.objects.get(id=subject_id)
            validated_data['subject'] = subject
        
        if 'faculty_id' in validated_data:
            faculty_id = validated_data.pop('faculty_id')
            if faculty_id:
                from apps.users.models import FacultyProfile
                faculty = FacultyProfile.objects.get(id=faculty_id)
                validated_data['faculty'] = faculty
            else:
                validated_data['faculty'] = None
        
        return super().update(instance, validated_data)


# Simplified serializers for basic operations
class DepartmentBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Department model without computed fields."""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class CourseBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Course model without nested data."""
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'department']


class SubjectBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Subject model without nested data."""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'course', 'semester']


class TimetableBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Timetable model without nested data."""
    
    class Meta:
        model = Timetable
        fields = ['id', 'class_name', 'subject', 'day_of_week', 'start_time', 'end_time']