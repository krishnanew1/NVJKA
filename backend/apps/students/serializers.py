"""
Serializers for the students app.

All date fields are explicitly formatted as ``YYYY-MM-DD`` to ensure
consistency regardless of the global DRF setting.
"""
from rest_framework import serializers
from .models import (
    Enrollment, AcademicHistory, SemesterRegistration,
    FeeTransaction, RegisteredCourse
)
from apps.academics.models import Course, Subject
from apps.users.serializers import UserBasicSerializer


class StudentNestedSerializer(serializers.Serializer):
    """
    Read-only nested representation of a StudentProfile embedded inside enrollment data.
    """
    id = serializers.IntegerField(read_only=True)
    enrollment_number = serializers.CharField(read_only=True)
    roll_number = serializers.CharField(read_only=True, source='enrollment_number')
    user = UserBasicSerializer(read_only=True)


class CourseNestedSerializer(serializers.Serializer):
    """
    Read-only nested representation of a Course embedded inside enrollment data.
    Exposes only the fields needed for display — id, name, and code.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the ``Enrollment`` model.

    Read:  ``course`` is returned as a nested object (id, name, code).
           ``student`` is returned as a nested object with user details.
    Write: ``course_id`` (integer FK) must be supplied instead.

    Validation ensures a student cannot be enrolled in the same course
    for the same semester twice (mirrors the ``unique_together`` DB constraint
    with a friendlier error message).
    """
    student = StudentNestedSerializer(read_only=True)
    course = CourseNestedSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True,
    )
    date_enrolled = serializers.DateField(format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_id', 'date_enrolled', 'status', 'semester']
        read_only_fields = ['date_enrolled']

    def validate(self, attrs):
        """Reject duplicate active enrollments at the serializer level."""
        student = attrs.get('student')
        course = attrs.get('course')
        semester = attrs.get('semester')
        qs = Enrollment.objects.filter(student=student, course=course, semester=semester)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'This student is already enrolled in this course for the given semester.'
            )
        return attrs


class AcademicHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the ``AcademicHistory`` model.

    Captures a student's prior academic record — institution, board/university,
    year of passing, and percentage or CGPA obtained.
    """
    class Meta:
        model = AcademicHistory
        fields = [
            'id', 'student', 'institution_name', 'board_university',
            'passing_year', 'percentage_cgpa',
        ]



class FeeTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for FeeTransaction model.
    
    Used as a nested serializer within SemesterRegistrationSerializer.
    Handles receipt image upload.
    """
    transaction_date = serializers.DateField(format='%Y-%m-%d')
    receipt_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = FeeTransaction
        fields = [
            'id', 'utr_no', 'bank_name', 'transaction_date',
            'amount', 'account_debited', 'account_credited',
            'receipt_image', 'receipt_url'
        ]
        read_only_fields = ['id']
    
    def get_receipt_url(self, obj):
        """Get the full URL for the receipt image."""
        if obj.receipt_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_image.url)
            return obj.receipt_image.url
        return None


class RegisteredCourseSerializer(serializers.ModelSerializer):
    """
    Serializer for RegisteredCourse model.
    
    Used as a nested serializer within SemesterRegistrationSerializer.
    For read operations, includes subject details.
    """
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source='subject',
        write_only=True
    )
    subject = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = RegisteredCourse
        fields = ['id', 'subject_id', 'subject', 'is_backlog']
        read_only_fields = ['id']
    
    def get_subject(self, obj):
        """Return subject details for read operations."""
        return {
            'id': obj.subject.id,
            'name': obj.subject.name,
            'code': obj.subject.code,
            'credits': obj.subject.credits,
            'semester': obj.subject.semester
        }


class SemesterRegistrationSerializer(serializers.ModelSerializer):
    """
    Nested serializer for SemesterRegistration with FeeTransactions and RegisteredCourses.
    
    Accepts a single POST request with:
    - Semester registration details
    - List of fee_transactions (up to 3)
    - List of registered_courses
    
    Validates that:
    - Maximum 3 fee transactions per registration
    - Student can only register their own semester
    """
    fee_transactions = FeeTransactionSerializer(many=True, required=False)
    registered_courses = RegisteredCourseSerializer(many=True, required=False)
    student_name = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SemesterRegistration
        fields = [
            'id', 'student', 'student_name', 'academic_year', 'semester',
            'institute_fee_paid', 'hostel_fee_paid', 'hostel_room_no',
            'total_credits', 'approval_status', 'approved_by', 'approved_by_name',
            'approved_at', 'admin_notes', 'fee_transactions', 'registered_courses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'approval_status', 'approved_by', 'approved_at', 
                           'admin_notes', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        """Return student's full name."""
        return obj.student.user.get_full_name() or obj.student.user.username
    
    def get_approved_by_name(self, obj):
        """Return approver's full name."""
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.username
        return None
    
    def validate_fee_transactions(self, value):
        """Validate that there are at most 3 fee transactions."""
        if len(value) > 3:
            raise serializers.ValidationError(
                'A semester registration cannot have more than 3 fee transactions.'
            )
        return value
    
    def create(self, validated_data):
        """Create semester registration with nested transactions and courses."""
        fee_transactions_data = validated_data.pop('fee_transactions', [])
        registered_courses_data = validated_data.pop('registered_courses', [])
        
        # Create the semester registration
        semester_registration = SemesterRegistration.objects.create(**validated_data)
        
        # Create fee transactions
        for transaction_data in fee_transactions_data:
            FeeTransaction.objects.create(
                semester_registration=semester_registration,
                **transaction_data
            )
        
        # Create registered courses
        for course_data in registered_courses_data:
            RegisteredCourse.objects.create(
                semester_registration=semester_registration,
                **course_data
            )
        
        return semester_registration
    
    def update(self, instance, validated_data):
        """Update semester registration and nested objects."""
        fee_transactions_data = validated_data.pop('fee_transactions', None)
        registered_courses_data = validated_data.pop('registered_courses', None)
        
        # Update semester registration fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update fee transactions if provided
        if fee_transactions_data is not None:
            # Delete existing transactions and create new ones
            instance.fee_transactions.all().delete()
            for transaction_data in fee_transactions_data:
                FeeTransaction.objects.create(
                    semester_registration=instance,
                    **transaction_data
                )
        
        # Update registered courses if provided
        if registered_courses_data is not None:
            # Delete existing courses and create new ones
            instance.registered_courses.all().delete()
            for course_data in registered_courses_data:
                RegisteredCourse.objects.create(
                    semester_registration=instance,
                    **course_data
                )
        
        return instance
