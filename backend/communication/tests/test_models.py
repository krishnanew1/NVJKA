from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from communication.models import Notice, Resource
from users.models import CustomUser
from academics.models import Department, Course, Subject


class NoticeModelTestCase(TestCase):
    """Test Notice model functionality"""

    def setUp(self):
        # Create users
        self.admin_user = CustomUser.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="testpass123",
            role="ADMIN"
        )
        
        self.student_user = CustomUser.objects.create_user(
            username="student1",
            email="student@example.com",
            password="testpass123",
            role="STUDENT"
        )
        
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1",
            email="faculty@example.com",
            password="testpass123",
            role="FACULTY"
        )

    def test_create_notice(self):
        """Test creating a basic notice"""
        notice = Notice.objects.create(
            title="Important Announcement",
            content="This is a test notice",
            created_by=self.admin_user,
            audience="ALL"
        )
        
        self.assertIsNotNone(notice.pk)
        self.assertEqual(notice.title, "Important Announcement")
        self.assertEqual(notice.audience, "ALL")
        self.assertTrue(notice.is_active)

    def test_notice_str_representation(self):
        """Test notice string representation"""
        notice = Notice.objects.create(
            title="Test Notice",
            content="Content",
            created_by=self.admin_user,
            audience="STUDENTS"
        )
        
        self.assertEqual(str(notice), "Test Notice (Students Only)")

    def test_notice_audience_choices(self):
        """Test all audience choices"""
        audiences = ['ALL', 'STUDENTS', 'FACULTY']
        
        for audience in audiences:
            notice = Notice.objects.create(
                title=f"Notice for {audience}",
                content="Test content",
                created_by=self.admin_user,
                audience=audience
            )
            self.assertEqual(notice.audience, audience)

    def test_notice_priority_levels(self):
        """Test all priority levels"""
        priorities = ['LOW', 'NORMAL', 'HIGH', 'URGENT']
        
        for priority in priorities:
            notice = Notice.objects.create(
                title=f"{priority} Priority Notice",
                content="Test content",
                created_by=self.admin_user,
                priority=priority
            )
            self.assertEqual(notice.priority, priority)

    def test_notice_default_values(self):
        """Test default field values"""
        notice = Notice.objects.create(
            title="Test Notice",
            content="Content",
            created_by=self.admin_user
        )
        
        self.assertEqual(notice.audience, "ALL")
        self.assertEqual(notice.priority, "NORMAL")
        self.assertTrue(notice.is_active)
        self.assertIsNone(notice.expires_at)

    def test_notice_visibility_to_all_users(self):
        """Test notice with ALL audience is visible to everyone"""
        notice = Notice.objects.create(
            title="Public Notice",
            content="For everyone",
            created_by=self.admin_user,
            audience="ALL"
        )
        
        self.assertTrue(notice.is_visible_to_user(self.admin_user))
        self.assertTrue(notice.is_visible_to_user(self.student_user))
        self.assertTrue(notice.is_visible_to_user(self.faculty_user))

    def test_notice_visibility_to_students_only(self):
        """Test notice with STUDENTS audience is visible only to students"""
        notice = Notice.objects.create(
            title="Student Notice",
            content="For students",
            created_by=self.admin_user,
            audience="STUDENTS"
        )
        
        self.assertFalse(notice.is_visible_to_user(self.admin_user))
        self.assertTrue(notice.is_visible_to_user(self.student_user))
        self.assertFalse(notice.is_visible_to_user(self.faculty_user))

    def test_notice_visibility_to_faculty_only(self):
        """Test notice with FACULTY audience is visible only to faculty"""
        notice = Notice.objects.create(
            title="Faculty Notice",
            content="For faculty",
            created_by=self.admin_user,
            audience="FACULTY"
        )
        
        self.assertFalse(notice.is_visible_to_user(self.admin_user))
        self.assertFalse(notice.is_visible_to_user(self.student_user))
        self.assertTrue(notice.is_visible_to_user(self.faculty_user))

    def test_inactive_notice_not_visible(self):
        """Test inactive notices are not visible"""
        notice = Notice.objects.create(
            title="Inactive Notice",
            content="Should not be visible",
            created_by=self.admin_user,
            audience="ALL",
            is_active=False
        )
        
        self.assertFalse(notice.is_visible_to_user(self.student_user))

    def test_expired_notice_not_visible(self):
        """Test expired notices are not visible"""
        past_time = timezone.now() - timedelta(days=1)
        
        notice = Notice.objects.create(
            title="Expired Notice",
            content="Should not be visible",
            created_by=self.admin_user,
            audience="ALL",
            expires_at=past_time
        )
        
        self.assertFalse(notice.is_visible_to_user(self.student_user))

    def test_future_expiry_notice_visible(self):
        """Test notices with future expiry are visible"""
        future_time = timezone.now() + timedelta(days=1)
        
        notice = Notice.objects.create(
            title="Future Notice",
            content="Should be visible",
            created_by=self.admin_user,
            audience="ALL",
            expires_at=future_time
        )
        
        self.assertTrue(notice.is_visible_to_user(self.student_user))

    def test_notice_ordering(self):
        """Test notices are ordered by created_at descending"""
        notice1 = Notice.objects.create(
            title="First",
            content="Content",
            created_by=self.admin_user
        )
        
        notice2 = Notice.objects.create(
            title="Second",
            content="Content",
            created_by=self.admin_user
        )
        
        notices = list(Notice.objects.all())
        self.assertEqual(notices[0], notice2)  # Most recent first
        self.assertEqual(notices[1], notice1)


class ResourceModelTestCase(TestCase):
    """Test Resource model functionality"""

    def setUp(self):
        # Create department
        self.department = Department.objects.create(
            name="Computer Science",
            code="CS"
        )

        # Create course
        self.course = Course.objects.create(
            name="B.Tech Computer Science",
            code="BTCS",
            department=self.department,
            credits=160,
            duration_years=4
        )

        # Create subject
        self.subject = Subject.objects.create(
            name="Data Structures",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4
        )

        # Create faculty user
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1",
            email="faculty@example.com",
            password="testpass123",
            role="FACULTY"
        )

    def test_create_resource(self):
        """Test creating a basic resource"""
        # Create a simple file
        file_content = b"Test file content"
        test_file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        
        resource = Resource.objects.create(
            title="Lecture Notes",
            description="Chapter 1 notes",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file,
            resource_type="NOTES"
        )
        
        self.assertIsNotNone(resource.pk)
        self.assertEqual(resource.title, "Lecture Notes")
        self.assertEqual(resource.resource_type, "NOTES")
        self.assertTrue(resource.is_active)

    def test_resource_str_representation(self):
        """Test resource string representation"""
        file_content = b"Test"
        test_file = SimpleUploadedFile("test.pdf", file_content)
        
        resource = Resource.objects.create(
            title="Test Resource",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file
        )
        
        self.assertEqual(str(resource), "Test Resource - CS201")

    def test_resource_file_size_auto_set(self):
        """Test file_size is automatically set on save"""
        file_content = b"Test file content with some data"
        test_file = SimpleUploadedFile("test.pdf", file_content)
        
        resource = Resource.objects.create(
            title="Test Resource",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file
        )
        
        self.assertEqual(resource.file_size, len(file_content))

    def test_resource_get_file_extension(self):
        """Test getting file extension"""
        test_file = SimpleUploadedFile("test.pdf", b"content")
        
        resource = Resource.objects.create(
            title="Test Resource",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file
        )
        
        self.assertEqual(resource.get_file_extension(), "PDF")

    def test_resource_get_file_size_display(self):
        """Test human-readable file size display"""
        # Test bytes
        resource = Resource(file_size=500)
        self.assertEqual(resource.get_file_size_display(), "500.0 B")
        
        # Test KB
        resource.file_size = 2048
        self.assertEqual(resource.get_file_size_display(), "2.0 KB")
        
        # Test MB
        resource.file_size = 5 * 1024 * 1024
        self.assertEqual(resource.get_file_size_display(), "5.0 MB")
        
        # Test GB
        resource.file_size = 2 * 1024 * 1024 * 1024
        self.assertEqual(resource.get_file_size_display(), "2.0 GB")

    def test_resource_increment_download_count(self):
        """Test incrementing download counter"""
        test_file = SimpleUploadedFile("test.pdf", b"content")
        
        resource = Resource.objects.create(
            title="Test Resource",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file
        )
        
        self.assertEqual(resource.download_count, 0)
        
        resource.increment_download_count()
        self.assertEqual(resource.download_count, 1)
        
        resource.increment_download_count()
        self.assertEqual(resource.download_count, 2)

    def test_resource_default_values(self):
        """Test default field values"""
        test_file = SimpleUploadedFile("test.pdf", b"content")
        
        resource = Resource.objects.create(
            title="Test Resource",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=test_file
        )
        
        self.assertEqual(resource.resource_type, "NOTES")
        self.assertEqual(resource.download_count, 0)
        self.assertTrue(resource.is_active)

    def test_resource_type_choices(self):
        """Test all resource type choices"""
        types = ['NOTES', 'ASSIGNMENT', 'REFERENCE', 'SLIDES', 'VIDEO', 'OTHER']
        
        for resource_type in types:
            test_file = SimpleUploadedFile(f"test_{resource_type}.pdf", b"content")
            resource = Resource.objects.create(
                title=f"Test {resource_type}",
                subject=self.subject,
                uploaded_by=self.faculty_user,
                file=test_file,
                resource_type=resource_type
            )
            self.assertEqual(resource.resource_type, resource_type)

    def test_resource_ordering(self):
        """Test resources are ordered by created_at descending"""
        file1 = SimpleUploadedFile("test1.pdf", b"content1")
        resource1 = Resource.objects.create(
            title="First",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=file1
        )
        
        file2 = SimpleUploadedFile("test2.pdf", b"content2")
        resource2 = Resource.objects.create(
            title="Second",
            subject=self.subject,
            uploaded_by=self.faculty_user,
            file=file2
        )
        
        resources = list(Resource.objects.all())
        self.assertEqual(resources[0], resource2)  # Most recent first
        self.assertEqual(resources[1], resource1)

    def test_resource_no_file_extension(self):
        """Test get_file_extension when no file"""
        resource = Resource(
            title="Test",
            subject=self.subject,
            uploaded_by=self.faculty_user
        )
        self.assertIsNone(resource.get_file_extension())

    def test_resource_no_file_size(self):
        """Test get_file_size_display when no file_size"""
        resource = Resource(
            title="Test",
            subject=self.subject,
            uploaded_by=self.faculty_user
        )
        self.assertEqual(resource.get_file_size_display(), "Unknown")
