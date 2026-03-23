"""
Serializers for the faculty app.
"""
from rest_framework import serializers
from .models import ClassAssignment
from apps.academics.models import Subject


class SubjectNestedSerializer(serializers.Serializer):
    """
    Read-only nested representation of a Subject embedded inside
    class-assignment data.  Exposes id, name, and code only.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)


class ClassAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the ``ClassAssignment`` model.

    Read:  ``subject`` is returned as a nested object (id, name, code).
    Write: ``subject_id`` (integer FK) must be supplied instead.

    The combination of (subject, semester, academic_year) must be unique —
    this is enforced at the database level via ``unique_together``.
    """
    subject = SubjectNestedSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source='subject',
        write_only=True,
    )

    class Meta:
        model = ClassAssignment
        fields = ['id', 'faculty', 'subject', 'subject_id', 'semester', 'academic_year']
