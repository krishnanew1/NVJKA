from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, GradeViewSet, StudentTranscriptView

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'grades', GradeViewSet, basename='grade')

app_name = 'exams'

urlpatterns = [
    path('', include(router.urls)),
    path('transcript/<int:student_id>/', StudentTranscriptView.as_view(), name='student_transcript'),
]
