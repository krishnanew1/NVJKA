from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EnrollmentViewSet, AcademicHistoryViewSet

app_name = 'students'

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'academic-history', AcademicHistoryViewSet, basename='academic-history')

urlpatterns = [
    path('', include(router.urls)),
]
