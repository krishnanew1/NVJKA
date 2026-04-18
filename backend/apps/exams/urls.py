from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssessmentViewSet, 
    GradeViewSet, 
    StudentTranscriptView,
    FacultyGradeManagementView,
    StudentMyGradesView,
    AdminSubjectGradesView
)

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'grades', GradeViewSet, basename='grade')

app_name = 'exams'

urlpatterns = [
    path('', include(router.urls)),
    path('transcript/<int:student_id>/', StudentTranscriptView.as_view(), name='student_transcript'),
    # StudentGrade management endpoints
    path('faculty/grades/', FacultyGradeManagementView.as_view(), name='faculty_grades'),
    path('students/my-grades/', StudentMyGradesView.as_view(), name='student_my_grades'),
    path('admin/subject-grades/', AdminSubjectGradesView.as_view(), name='admin_subject_grades'),
]
