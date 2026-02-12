from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import time
from academics.models import Department, Course, Subject, Timetable


class TimetableConflictTestCase(TestCase):
    """Test timetable scheduling conflict validation"""

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

        # Create subjects
        self.subject1 = Subject.objects.create(
            name="Data Structures",
            code="CS201",
            course=self.course,
            semester=3,
            credits=4
        )
        
        self.subject2 = Subject.objects.create(
            name="Algorithms",
            code="CS202",
            course=self.course,
            semester=3,
            credits=3
        )

    def test_valid_timetable_entry(self):
        """Test creating a valid timetable entry"""
        timetable = Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        self.assertIsNotNone(timetable.pk)

    def test_end_time_before_start_time_raises_error(self):
        """Test that end_time before start_time raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-A",
                subject=self.subject1,
                day_of_week="MONDAY",
                start_time=time(10, 0),
                end_time=time(9, 0),  # Before start time
                room_number="101",
                academic_year="2024-25"
            )
        
        self.assertIn('end_time', context.exception.message_dict)

    def test_end_time_equal_to_start_time_raises_error(self):
        """Test that end_time equal to start_time raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-A",
                subject=self.subject1,
                day_of_week="MONDAY",
                start_time=time(9, 0),
                end_time=time(9, 0),  # Same as start time
                room_number="101",
                academic_year="2024-25"
            )
        
        self.assertIn('end_time', context.exception.message_dict)

    def test_exact_same_time_slot_conflict(self):
        """Test that exact same time slot in same room raises conflict"""
        # Create first entry
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Try to create conflicting entry
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-B",
                subject=self.subject2,
                day_of_week="MONDAY",
                start_time=time(9, 0),
                end_time=time(10, 0),
                room_number="101",  # Same room
                academic_year="2024-25"
            )
        
        self.assertIn('room_number', context.exception.message_dict)

    def test_overlapping_time_slots_conflict(self):
        """Test that overlapping time slots in same room raise conflict"""
        # Create first entry: 9:00-10:30
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="TUESDAY",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room_number="102",
            academic_year="2024-25"
        )
        
        # Try to create overlapping entry: 10:00-11:00
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-B",
                subject=self.subject2,
                day_of_week="TUESDAY",
                start_time=time(10, 0),  # Overlaps with 9:00-10:30
                end_time=time(11, 0),
                room_number="102",  # Same room
                academic_year="2024-25"
            )
        
        self.assertIn('room_number', context.exception.message_dict)

    def test_contained_time_slot_conflict(self):
        """Test that a time slot contained within another raises conflict"""
        # Create first entry: 9:00-12:00
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="WEDNESDAY",
            start_time=time(9, 0),
            end_time=time(12, 0),
            room_number="103",
            academic_year="2024-25"
        )
        
        # Try to create contained entry: 10:00-11:00
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-B",
                subject=self.subject2,
                day_of_week="WEDNESDAY",
                start_time=time(10, 0),  # Inside 9:00-12:00
                end_time=time(11, 0),
                room_number="103",  # Same room
                academic_year="2024-25"
            )
        
        self.assertIn('room_number', context.exception.message_dict)

    def test_containing_time_slot_conflict(self):
        """Test that a time slot containing another raises conflict"""
        # Create first entry: 10:00-11:00
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="THURSDAY",
            start_time=time(10, 0),
            end_time=time(11, 0),
            room_number="104",
            academic_year="2024-25"
        )
        
        # Try to create containing entry: 9:00-12:00
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-B",
                subject=self.subject2,
                day_of_week="THURSDAY",
                start_time=time(9, 0),  # Contains 10:00-11:00
                end_time=time(12, 0),
                room_number="104",  # Same room
                academic_year="2024-25"
            )
        
        self.assertIn('room_number', context.exception.message_dict)

    def test_adjacent_time_slots_no_conflict(self):
        """Test that adjacent time slots (no overlap) don't conflict"""
        # Create first entry: 9:00-10:00
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="FRIDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="105",
            academic_year="2024-25"
        )
        
        # Create adjacent entry: 10:00-11:00 (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="FRIDAY",
            start_time=time(10, 0),  # Starts when previous ends
            end_time=time(11, 0),
            room_number="105",  # Same room
            academic_year="2024-25"
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_different_rooms_no_conflict(self):
        """Test that same time slot in different rooms don't conflict"""
        # Create first entry in room 101
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Create same time slot in room 102 (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="102",  # Different room
            academic_year="2024-25"
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_different_days_no_conflict(self):
        """Test that same time slot on different days don't conflict"""
        # Create entry on Monday
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Create same time slot on Tuesday (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="TUESDAY",  # Different day
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",  # Same room
            academic_year="2024-25"
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_different_academic_years_no_conflict(self):
        """Test that same time slot in different academic years don't conflict"""
        # Create entry for 2024-25
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Create same time slot for 2025-26 (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",  # Same room
            academic_year="2025-26"  # Different year
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_inactive_entry_no_conflict(self):
        """Test that inactive entries don't cause conflicts"""
        # Create inactive entry
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25",
            is_active=False  # Inactive
        )
        
        # Create active entry at same time (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",  # Same room
            academic_year="2024-25",
            is_active=True
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_no_room_number_no_conflict_check(self):
        """Test that entries without room_number don't trigger conflict check"""
        # Create first entry without room
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number=None,
            academic_year="2024-25"
        )
        
        # Create second entry without room at same time (should succeed)
        timetable = Timetable.objects.create(
            class_name="CS-B",
            subject=self.subject2,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number=None,
            academic_year="2024-25"
        )
        
        self.assertIsNotNone(timetable.pk)

    def test_update_existing_entry_no_self_conflict(self):
        """Test that updating an entry doesn't conflict with itself"""
        # Create entry
        timetable = Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 0),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Update the same entry (should succeed)
        timetable.class_name = "CS-A-Updated"
        timetable.save()
        
        self.assertEqual(timetable.class_name, "CS-A-Updated")

    def test_conflict_error_message_contains_details(self):
        """Test that conflict error message contains helpful details"""
        # Create first entry
        Timetable.objects.create(
            class_name="CS-A",
            subject=self.subject1,
            day_of_week="MONDAY",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room_number="101",
            academic_year="2024-25"
        )
        
        # Try to create conflicting entry
        with self.assertRaises(ValidationError) as context:
            Timetable.objects.create(
                class_name="CS-B",
                subject=self.subject2,
                day_of_week="MONDAY",
                start_time=time(10, 0),
                end_time=time(11, 0),
                room_number="101",
                academic_year="2024-25"
            )
        
        error_message = str(context.exception.message_dict['room_number'][0])
        
        # Verify error message contains useful information
        self.assertIn("101", error_message)  # Room number
        self.assertIn("MONDAY", error_message)  # Day
        self.assertIn("09:00", error_message)  # Start time
        self.assertIn("10:30", error_message)  # End time
        self.assertIn("CS-A", error_message)  # Class name
        self.assertIn("CS201", error_message)  # Subject code

    def test_multiple_non_conflicting_entries(self):
        """Test creating multiple non-conflicting entries"""
        entries = [
            ("CS-A", self.subject1, "MONDAY", time(9, 0), time(10, 0), "101"),
            ("CS-B", self.subject2, "MONDAY", time(10, 0), time(11, 0), "101"),
            ("CS-C", self.subject1, "MONDAY", time(11, 0), time(12, 0), "101"),
            ("CS-D", self.subject2, "TUESDAY", time(9, 0), time(10, 0), "101"),
            ("CS-E", self.subject1, "MONDAY", time(9, 0), time(10, 0), "102"),
        ]
        
        for class_name, subject, day, start, end, room in entries:
            timetable = Timetable.objects.create(
                class_name=class_name,
                subject=subject,
                day_of_week=day,
                start_time=start,
                end_time=end,
                room_number=room,
                academic_year="2024-25"
            )
            self.assertIsNotNone(timetable.pk)
        
        self.assertEqual(Timetable.objects.count(), 5)
