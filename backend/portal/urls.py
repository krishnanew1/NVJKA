from django.urls import path
from . import views

urlpatterns = [
    # Keep your existing home page if you want
    path('', views.home, name='home'), 
    
    # Add the new dashboard URL
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
]