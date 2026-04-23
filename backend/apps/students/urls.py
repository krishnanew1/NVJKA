from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    EnrollmentViewSet, AcademicHistoryViewSet,
    SemesterRegistrationViewSet, RegistrationTrackingView,
    StudentRegistrationDetailView, ApproveRegistrationView,
    RegistrationOptionsView
)

app_name = 'students'

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'academic-history', AcademicHistoryViewSet, basename='academic-history')
router.register(r'semester-register', SemesterRegistrationViewSet, basename='semester-register')

urlpatterns = [
    path('', include(router.urls)),
    path('registration-tracking/', RegistrationTrackingView.as_view(), name='registration-tracking'),
    path('registration-options/', RegistrationOptionsView.as_view(), name='registration-options'),
    path('registration-detail/<int:student_id>/<int:registration_id>/', 
         StudentRegistrationDetailView.as_view(), 
         name='registration-detail'),
    path('approve-registration/', ApproveRegistrationView.as_view(), name='approve-registration'),
]
