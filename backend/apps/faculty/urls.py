from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ClassAssignmentViewSet

app_name = 'faculty'

router = DefaultRouter()
router.register(r'assignments', ClassAssignmentViewSet, basename='classassignment')

urlpatterns = [
    path('', include(router.urls)),
]
