"""
Serializers for the students app.

All date fields are explicitly formatted as ``YYYY-MM-DD`` to ensure
consistency regardless of the global DRF setting.
"""
from rest_framework import serializers
from .models import Enrollment, AcademicHistory
from apps.academics.models import Course


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
    Write: ``course_id`` (integer FK) must be supplied instead.

    Validation ensures a student cannot be enrolled in the same course
    for the same semester twice (mirrors the ``unique_together`` DB constraint
    with a friendlier error message).
    """
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
