# Timetable Conflict Prevention Documentation

## Overview

The Timetable model includes comprehensive validation to prevent scheduling conflicts. The system ensures that no two classes can be scheduled in the same classroom at overlapping times, preventing double-booking and scheduling errors.

## Features

### 1. Time Validation

Ensures that class end time is after start time.

**Validation:**
- `end_time` must be greater than `start_time`
- Equal times are not allowed (class must have duration)

**Example Error:**
```python
# This will raise ValidationError
Timetable.objects.create(
    class_name="CS-A",
    subject=subject,
    day_of_week="MONDAY",
    start_time=time(10, 0),
    end_time=time(9, 0),  # Before start time - ERROR
    room_number="101",
    academic_year="2024-25"
)
```

### 2. Classroom Conflict Detection

Prevents double-booking of classrooms by detecting time slot overlaps.

**Conflict Detection Logic:**

Two time slots overlap if:
```
(start1 < end2) AND (end1 > start2)
```

This formula catches all overlap scenarios:
- Exact same time slot
- Partial overlap
- One slot contained within another
- One slot containing another

**Conflict Scenarios Detected:**

1. **Exact Same Time Slot**
   ```
   Existing: 9:00 - 10:00
   New:      9:00 - 10:00  ❌ CONFLICT
   ```

2. **Partial Overlap**
   ```
   Existing: 9:00 - 10:30
   New:     10:00 - 11:00  ❌ CONFLICT
   ```

3. **Contained Time Slot**
   ```
   Existing: 9:00 - 12:00
   New:     10:00 - 11:00  ❌ CONFLICT
   ```

4. **Containing Time Slot**
   ```
   Existing: 10:00 - 11:00
   New:       9:00 - 12:00  ❌ CONFLICT
   ```

**Non-Conflict Scenarios:**

1. **Adjacent Time Slots**
   ```
   Existing: 9:00 - 10:00
   New:     10:00 - 11:00  ✓ OK (no overlap)
   ```

2. **Different Rooms**
   ```
   Existing: Room 101, 9:00 - 10:00
   New:      Room 102, 9:00 - 10:00  ✓ OK
   ```

3. **Different Days**
   ```
   Existing: Monday, 9:00 - 10:00
   New:      Tuesday, 9:00 - 10:00  ✓ OK
   ```

4. **Different Academic Years**
   ```
   Existing: 2024-25, 9:00 - 10:00
   New:      2025-26, 9:00 - 10:00  ✓ OK
   ```

### 3. Conflict Checking Conditions

Conflict validation only runs when ALL of the following are present:
- `room_number` is specified (not null/empty)
- `day_of_week` is specified
- `start_time` is specified
- `end_time` is specified
- `academic_year` is specified

**Rationale:** If no room is assigned, there's no physical space conflict to check.

### 4. Active Status Filtering

Only active timetable entries (`is_active=True`) are checked for conflicts.

**Use Case:** Allows keeping historical or cancelled entries without causing conflicts.

```python
# Inactive entry doesn't cause conflict
Timetable.objects.create(
    room_number="101",
    day_of_week="MONDAY",
    start_time=time(9, 0),
    end_time=time(10, 0),
    is_active=False  # Won't block new entries
)

# This will succeed
Timetable.objects.create(
    room_number="101",
    day_of_week="MONDAY",
    start_time=time(9, 0),
    end_time=time(10, 0),
    is_active=True  # OK - previous entry is inactive
)
```

### 5. Update Protection

When updating an existing timetable entry, the validation excludes the current instance from conflict checking.

**Prevents:** False positives where an entry would conflict with itself.

```python
# Create entry
timetable = Timetable.objects.create(
    class_name="CS-A",
    room_number="101",
    day_of_week="MONDAY",
    start_time=time(9, 0),
    end_time=time(10, 0)
)

# Update same entry - no conflict with itself
timetable.class_name = "CS-A-Updated"
timetable.save()  # ✓ OK
```

## Implementation Details

### Model Validation

The `clean()` method in the Timetable model performs all validation:

```python
def clean(self):
    """
    Validate timetable entry:
    1. End time must be after start time
    2. No classroom conflicts (same room at overlapping times)
    """
    from django.core.exceptions import ValidationError
    from django.db.models import Q
    
    errors = {}
    
    # Time validation
    if self.start_time and self.end_time:
        if self.start_time >= self.end_time:
            errors['end_time'] = "End time must be after start time."
    
    # Conflict detection
    if self.room_number and self.day_of_week and self.start_time and self.end_time:
        conflicts = Timetable.objects.filter(
            room_number=self.room_number,
            day_of_week=self.day_of_week,
            academic_year=self.academic_year,
            is_active=True
        )
        
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)
        
        overlapping = conflicts.filter(
            Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)
        )
        
        if overlapping.exists():
            conflicting_entry = overlapping.first()
            errors['room_number'] = (
                f"Room {self.room_number} is already booked on {self.day_of_week} "
                f"from {conflicting_entry.start_time.strftime('%H:%M')} to "
                f"{conflicting_entry.end_time.strftime('%H:%M')} "
                f"for {conflicting_entry.class_name} ({conflicting_entry.subject.code})."
            )
    
    if errors:
        raise ValidationError(errors)
```

### Automatic Validation

The `save()` method is overridden to automatically call `clean()`:

```python
def save(self, *args, **kwargs):
    """Override save to call clean() for validation."""
    self.clean()
    super().save(*args, **kwargs)
```

This ensures validation runs on every save operation, including:
- Direct model creation
- Admin panel saves
- API endpoint saves
- Bulk operations (if using `save()`)

## Error Messages

### Time Validation Error

```
ValidationError: {'end_time': ['End time must be after start time.']}
```

### Conflict Error

```
ValidationError: {
    'room_number': [
        'Room 101 is already booked on MONDAY from 09:00 to 10:30 
         for CS-A (CS201).'
    ]
}
```

The conflict error message includes:
- Room number
- Day of week
- Conflicting time slot (start and end)
- Conflicting class name
- Conflicting subject code

## Database Constraints

### Unique Together Constraints

The model includes database-level unique constraints:

```python
unique_together = [
    ['class_name', 'day_of_week', 'start_time', 'academic_year'],
    ['subject', 'class_name', 'day_of_week', 'start_time', 'academic_year']
]
```

**Purpose:** Prevents duplicate entries for the same class at the same time.

**Note:** These constraints are separate from room conflict validation.

## Testing

The system includes comprehensive tests covering all scenarios.

### Test Coverage (16 tests)

1. **Valid Entry Creation**: Basic timetable entry creation
2. **Time Validation**: End time before/equal to start time
3. **Exact Conflict**: Same time slot in same room
4. **Overlapping Conflict**: Partial time overlap
5. **Contained Conflict**: Slot within another slot
6. **Containing Conflict**: Slot containing another slot
7. **Adjacent Slots**: No conflict for back-to-back classes
8. **Different Rooms**: Same time, different rooms
9. **Different Days**: Same time, different days
10. **Different Years**: Same time, different academic years
11. **Inactive Entries**: Inactive entries don't cause conflicts
12. **No Room Number**: Entries without rooms don't conflict
13. **Update Protection**: Updating entry doesn't self-conflict
14. **Error Messages**: Conflict messages contain details
15. **Multiple Entries**: Creating multiple valid entries
16. **Self-Update**: Updating existing entry succeeds

### Running Tests

```bash
# Run timetable conflict tests
python manage.py test academics.tests.test_timetable_conflicts

# Run all academics tests
python manage.py test academics
```

## Usage Examples

### Creating Valid Timetable Entries

```python
from datetime import time
from academics.models import Timetable, Subject

# Create non-conflicting schedule
schedule = [
    {
        'class_name': 'CS-A',
        'subject': subject1,
        'day_of_week': 'MONDAY',
        'start_time': time(9, 0),
        'end_time': time(10, 0),
        'room_number': '101',
        'academic_year': '2024-25'
    },
    {
        'class_name': 'CS-B',
        'subject': subject2,
        'day_of_week': 'MONDAY',
        'start_time': time(10, 0),  # Adjacent, no overlap
        'end_time': time(11, 0),
        'room_number': '101',
        'academic_year': '2024-25'
    },
    {
        'class_name': 'CS-C',
        'subject': subject3,
        'day_of_week': 'MONDAY',
        'start_time': time(9, 0),  # Same time, different room
        'end_time': time(10, 0),
        'room_number': '102',
        'academic_year': '2024-25'
    }
]

for entry in schedule:
    Timetable.objects.create(**entry)
```

### Handling Conflicts

```python
from django.core.exceptions import ValidationError

try:
    Timetable.objects.create(
        class_name='CS-D',
        subject=subject,
        day_of_week='MONDAY',
        start_time=time(9, 30),  # Overlaps with existing
        end_time=time(10, 30),
        room_number='101',
        academic_year='2024-25'
    )
except ValidationError as e:
    print(f"Scheduling conflict: {e.message_dict['room_number'][0]}")
    # Handle conflict - suggest alternative room or time
```

## API Integration

When creating API endpoints for timetable management:

```python
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from django.core.exceptions import ValidationError

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'
    
    def validate(self, data):
        """Run model validation in serializer"""
        instance = Timetable(**data)
        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
```

## Performance Considerations

### Query Optimization

The conflict detection query is optimized:
- Filters by room, day, year, and active status first
- Uses indexed fields for filtering
- Only checks time overlap on pre-filtered results
- Excludes current instance efficiently

### Database Indexes

Consider adding indexes for frequently queried fields:

```python
class Meta:
    indexes = [
        models.Index(fields=['room_number', 'day_of_week', 'academic_year']),
        models.Index(fields=['is_active']),
    ]
```

## Future Enhancements

Potential improvements:
1. Faculty conflict detection (same faculty, overlapping times)
2. Student group conflict detection (same students, overlapping classes)
3. Bulk scheduling with conflict resolution
4. Automatic alternative room/time suggestions
5. Visual timetable conflict preview
6. Conflict resolution workflow
7. Room capacity validation
8. Equipment/resource conflict checking

## Related Documentation

- [Academics Models](academics/models.py)
- [Timetable Conflict Tests](academics/tests/test_timetable_conflicts.py)
- [Academic Structure Documentation](academics/README.md)
