from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.users.models import StudentProfile, FacultyProfile
from apps.academics.models import Subject


class Assessment(models.Model):
    """
    Assessment model representing exams, quizzes, assignments, etc.
    Defines the evaluation criteria for a subject.
    """
    
    ASSESSMENT_TYPE_CHOICES = [
        ('EXAM', 'Examination'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('LAB', 'Lab Work'),
        ('PRESENTATION', 'Presentation'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Name of the assessment (e.g., Midterm Exam, Quiz 1)'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assessments',
        help_text='Subject for which this assessment is conducted'
    )
    
    assessment_type = models.CharField(
        max_length=20,
        choices=ASSESSMENT_TYPE_CHOICES,
        default='EXAM',
        help_text='Type of assessment'
    )
    
    max_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Maximum marks for this assessment'
    )
    
    weightage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Weightage percentage in final grade (0-100)'
    )
    
    date_conducted = models.DateField(
        null=True,
        blank=True,
        help_text='Date when assessment was conducted'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Additional details about the assessment'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
        ordering = ['-date_conducted', 'subject', 'name']
        unique_together = ['subject', 'name']
    
    def __str__(self):
        return f"{self.subject.code} - {self.name} ({self.max_marks} marks)"
    
    def clean(self):
        """Validate assessment data."""
        super().clean()
        
        if self.max_marks and self.max_marks <= 0:
            raise ValidationError({
                'max_marks': 'Maximum marks must be greater than 0'
            })
        
        if self.weightage and (self.weightage < 0 or self.weightage > 100):
            raise ValidationError({
                'weightage': 'Weightage must be between 0 and 100'
            })


class Grade(models.Model):
    """
    Grade model storing student marks for assessments.
    Links students to their performance in specific assessments.
    """
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='grades',
        help_text='Student who received this grade'
    )
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='grades',
        help_text='Assessment for which grade is given'
    )
    
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Marks obtained by the student'
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Additional remarks or feedback'
    )
    
    graded_by = models.ForeignKey(
        'users.FacultyProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_assessments',
        help_text='Faculty member who graded this assessment'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        ordering = ['-created_at']
        unique_together = ['student', 'assessment']
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.assessment.name}: {self.marks_obtained}/{self.assessment.max_marks}"
    
    def clean(self):
        """
        Validate that marks_obtained does not exceed assessment.max_marks.
        """
        super().clean()
        
        if self.marks_obtained is not None and self.assessment:
            if self.marks_obtained < 0:
                raise ValidationError({
                    'marks_obtained': 'Marks obtained cannot be negative'
                })
            
            if self.marks_obtained > self.assessment.max_marks:
                raise ValidationError({
                    'marks_obtained': f'Marks obtained ({self.marks_obtained}) cannot exceed maximum marks ({self.assessment.max_marks})'
                })
    
    def save(self, *args, **kwargs):
        """Override save to call clean() for validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.assessment.max_marks > 0:
            return (self.marks_obtained / self.assessment.max_marks) * 100
        return 0.0
    
    @property
    def weighted_marks(self):
        """Calculate weighted marks based on assessment weightage."""
        return (self.percentage * self.assessment.weightage) / 100
    
    def get_letter_grade(self):
        """
        Get letter grade based on percentage.
        Standard grading scale: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)
        """
        percentage = self.percentage
        
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'



class StudentGrade(models.Model):
    """
    StudentGrade model for storing final subject grades.
    Represents the overall grade for a student in a subject.
    """
    
    GRADE_CHOICES = [
        ('A+', 'A+ (Outstanding)'),
        ('A', 'A (Excellent)'),
        ('B+', 'B+ (Very Good)'),
        ('B', 'B (Good)'),
        ('C+', 'C+ (Above Average)'),
        ('C', 'C (Average)'),
        ('D', 'D (Pass)'),
        ('F', 'F (Fail)'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='subject_grades',
        help_text='Student receiving the grade'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_grades',
        help_text='Subject for which grade is given'
    )
    
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_students',
        help_text='Faculty member who assigned the grade'
    )
    
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Total marks obtained by the student'
    )
    
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Total maximum marks for the subject'
    )
    
    grade_letter = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        help_text='Letter grade (A+, A, B+, B, C+, C, D, F)'
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text='Additional remarks or feedback'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Student Grade'
        verbose_name_plural = 'Student Grades'
        ordering = ['-created_at']
        unique_together = ['student', 'subject']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['subject']),
            models.Index(fields=['grade_letter']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.subject.code}: {self.grade_letter}"
    
    def clean(self):
        """Validate grade data."""
        super().clean()
        
        if self.marks_obtained is not None and self.marks_obtained < 0:
            raise ValidationError({
                'marks_obtained': 'Marks obtained cannot be negative'
            })
        
        if self.total_marks is not None and self.total_marks <= 0:
            raise ValidationError({
                'total_marks': 'Total marks must be greater than 0'
            })
        
        if self.marks_obtained is not None and self.total_marks is not None:
            if self.marks_obtained > self.total_marks:
                raise ValidationError({
                    'marks_obtained': f'Marks obtained ({self.marks_obtained}) cannot exceed total marks ({self.total_marks})'
                })
    
    def save(self, *args, **kwargs):
        """Override save to call clean() for validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.total_marks > 0:
            return round((self.marks_obtained / self.total_marks) * 100, 2)
        return 0.0
    
    @property
    def grade_point(self):
        """
        Get grade point based on letter grade.
        A+ = 10, A = 9, B+ = 8, B = 7, C+ = 6, C = 5, D = 4, F = 0
        """
        grade_points = {
            'A+': 10,
            'A': 9,
            'B+': 8,
            'B': 7,
            'C+': 6,
            'C': 5,
            'D': 4,
            'F': 0,
        }
        return grade_points.get(self.grade_letter, 0)
    
    @staticmethod
    def calculate_letter_grade(percentage):
        """
        Calculate letter grade from percentage.
        A+ (95-100), A (90-94), B+ (85-89), B (80-84), 
        C+ (75-79), C (70-74), D (60-69), F (<60)
        """
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'B+'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 75:
            return 'C+'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
