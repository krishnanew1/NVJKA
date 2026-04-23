from rest_framework import serializers

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id',
            'created_by',
            'subject',
            'department',
            'batch_year',
            'semester',
            'section',
            'title',
            'description',
            'due_at',
            'requires_submission',
            'allow_late',
            'attachment',
            'attachment_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'attachment_url']

    def get_created_by(self, obj):
        u = obj.created_by
        return {
            'id': u.id,
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'role': getattr(u, 'role', None),
        }

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if not obj.attachment:
            return None
        if request:
            return request.build_absolute_uri(obj.attachment.url)
        return obj.attachment.url


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id',
            'assignment',
            'student',
            'file',
            'file_url',
            'text_answer',
            'submitted_at',
            'is_late',
        ]
        read_only_fields = ['id', 'student', 'submitted_at', 'is_late', 'file_url', 'assignment']

    def get_student(self, obj):
        sp = obj.student
        u = sp.user
        return {
            'id': sp.id,
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'reg_no': getattr(sp, 'reg_no', None) or getattr(sp, 'enrollment_number', None),
            'batch_year': getattr(sp, 'batch_year', None),
            'current_semester': getattr(sp, 'current_semester', None),
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def get_is_late(self, obj):
        return obj.is_late


class AssignmentSubmitSerializer(serializers.Serializer):
    file = serializers.FileField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('file') and not attrs.get('text_answer'):
            raise serializers.ValidationError('Provide either a file or a text_answer.')
        return attrs
