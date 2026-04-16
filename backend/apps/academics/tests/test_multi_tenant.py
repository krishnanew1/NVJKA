"""
Tests for multi-tenant features: CustomRegistrationField and Program models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.academics.models import Department, CustomRegistrationField, Program
from apps.users.models import StudentProfile

User = get_user_model()


class CustomRegistrationFieldTests(TestCase):
    """Test cases for CustomRegistrationField model."""
    
    def setUp(self):
        """Set up test data."""
        self.field_data = {
            'field_name': 'aadhar_number',
            'field_label': 'Aadhar Number',
            'field_type': 'text',
            'is_required': True,
            'placeholder': '1234-5678-9012',
            'help_text': 'Enter your 12-digit Aadhar number',
            'order': 1
        }
    
    def test_create_custom_field(self):
        """Test creating a custom registration field."""
        field = CustomRegistrationField.objects.create(**self.field_data)
        
        self.assertEqual(field.field_name, 'aadhar_number')
        self.assertEqual(field.field_label, 'Aadhar Number')
        self.assertEqual(field.field_type, 'text')
        self.assertTrue(field.is_required)
        self.assertTrue(field.is_active)
    
    def test_dropdown_field_with_options(self):
        """Test creating a dropdown field with options."""
        field = CustomRegistrationField.objects.create(
            field_name='blood_group',
            field_label='Blood Group',
            field_type='dropdown',
            dropdown_options='A+,A-,B+,B-,AB+,AB-,O+,O-',
            is_required=False,
            order=2
        )
        
        self.assertEqual(field.field_type, 'dropdown')
        self.assertIsNotNone(field.dropdown_options)
        self.assertIn('A+', field.dropdown_options)
    
    def test_field_ordering(self):
        """Test that fields are ordered correctly."""
        field1 = CustomRegistrationField.objects.create(
            field_name='field1',
            field_label='Field 1',
            field_type='text',
            order=2
        )
        field2 = CustomRegistrationField.objects.create(
            field_name='field2',
            field_label='Field 2',
            field_type='text',
            order=1
        )
        
        fields = list(CustomRegistrationField.objects.all())
        self.assertEqual(fields[0], field2)  # Lower order comes first
        self.assertEqual(fields[1], field1)
    
    def test_active_inactive_fields(self):
        """Test filtering active and inactive fields."""
        active_field = CustomRegistrationField.objects.create(
            field_name='active_field',
            field_label='Active Field',
            field_type='text',
            is_active=True
        )
        inactive_field = CustomRegistrationField.objects.create(
            field_name='inactive_field',
            field_label='Inactive Field',
            field_type='text',
            is_active=False
        )
        
        active_fields = CustomRegistrationField.objects.filter(is_active=True)
        self.assertIn(active_field, active_fields)
        self.assertNotIn(inactive_field, active_fields)


class ProgramTests(TestCase):
    """Test cases for Program model."""
    
    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            description='Computer Science Department'
        )
    
    def test_create_program(self):
        """Test creating a program."""
        program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.department,
            duration_years=4,
            duration_semesters=8,
            total_credits=160,
            description='4-year undergraduate program'
        )
        
        self.assertEqual(program.name, 'Bachelor of Technology')
        self.assertEqual(program.code, 'BTECH')
        self.assertEqual(program.department, self.department)
        self.assertEqual(program.duration_years, 4)
        self.assertEqual(program.duration_semesters, 8)
        self.assertTrue(program.is_active)
    
    def test_auto_calculate_semesters(self):
        """Test that semesters are auto-calculated from years."""
        program = Program.objects.create(
            name='Master of Science',
            code='MSC',
            department=self.department,
            duration_years=2,
            total_credits=80
        )
        
        # Semesters should be auto-calculated as years * 2
        self.assertEqual(program.duration_semesters, 4)
    
    def test_program_string_representation(self):
        """Test program string representation."""
        program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.department,
            duration_years=4,
            duration_semesters=8
        )
        
        self.assertEqual(str(program), 'BTECH - Bachelor of Technology')
    
    def test_program_department_relationship(self):
        """Test program-department relationship."""
        program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.department,
            duration_years=4,
            duration_semesters=8
        )
        
        # Check reverse relationship
        self.assertIn(program, self.department.programs.all())


class StudentProfileCustomDataTests(TestCase):
    """Test cases for StudentProfile custom_data field."""
    
    def setUp(self):
        """Set up test data."""
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTECH',
            department=self.department,
            duration_years=4,
            duration_semesters=8
        )
        self.user = User.objects.create_user(
            username='john_doe',
            email='john@example.com',
            password='testpass123',
            role='STUDENT'
        )
    
    def test_create_student_with_custom_data(self):
        """Test creating a student profile with custom data."""
        custom_data = {
            'aadhar_number': '1234-5678-9012',
            'samagra_id': 'ABC123456',
            'blood_group': 'O+',
            'parent_phone': '+91-9876543210'
        }
        
        student = StudentProfile.objects.create(
            user=self.user,
            reg_no='2026CS001',
            enrollment_number='2026CS001',
            dob='2005-05-15',
            gender='M',
            phone='+91-9876543210',
            address='123 Main St',
            program=self.program,
            department=self.department,
            current_semester=1,
            batch_year=2026,
            custom_data=custom_data
        )
        
        self.assertEqual(student.custom_data['aadhar_number'], '1234-5678-9012')
        self.assertEqual(student.custom_data['samagra_id'], 'ABC123456')
        self.assertEqual(student.custom_data['blood_group'], 'O+')
    
    def test_update_custom_data(self):
        """Test updating custom data."""
        student = StudentProfile.objects.create(
            user=self.user,
            reg_no='2026CS001',
            enrollment_number='2026CS001',
            program=self.program,
            department=self.department,
            current_semester=1,
            batch_year=2026,
            custom_data={'aadhar_number': '1234-5678-9012'}
        )
        
        # Update custom data
        student.custom_data['blood_group'] = 'A+'
        student.save()
        
        # Refresh from database
        student.refresh_from_db()
        self.assertEqual(student.custom_data['blood_group'], 'A+')
        self.assertEqual(student.custom_data['aadhar_number'], '1234-5678-9012')
    
    def test_empty_custom_data(self):
        """Test that custom_data defaults to empty dict."""
        student = StudentProfile.objects.create(
            user=self.user,
            reg_no='2026CS001',
            enrollment_number='2026CS001',
            program=self.program,
            department=self.department,
            current_semester=1,
            batch_year=2026
        )
        
        self.assertEqual(student.custom_data, {})
        self.assertIsInstance(student.custom_data, dict)
    
    def test_student_program_relationship(self):
        """Test student-program relationship."""
        student = StudentProfile.objects.create(
            user=self.user,
            reg_no='2026CS001',
            enrollment_number='2026CS001',
            program=self.program,
            department=self.department,
            current_semester=1,
            batch_year=2026
        )
        
        self.assertEqual(student.program, self.program)
        self.assertIn(student, self.program.students.all())
    
    def test_reg_no_enrollment_number_sync(self):
        """Test that reg_no and enrollment_number are synced."""
        student = StudentProfile.objects.create(
            user=self.user,
            reg_no='2026CS001',
            program=self.program,
            department=self.department,
            current_semester=1,
            batch_year=2026
        )
        
        # enrollment_number should be auto-set from reg_no
        self.assertEqual(student.enrollment_number, student.reg_no)
