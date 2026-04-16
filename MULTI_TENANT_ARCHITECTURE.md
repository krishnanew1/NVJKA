# Multi-Tenant Architecture - Dynamic Registration Fields

## 🎯 Overview

The Academic ERP system has been transformed into a multi-tenant, flexible platform that supports dynamic registration fields and programs. This allows any college or institution to customize the system without code changes.

---

## 🏗️ Architecture Changes

### 1. CustomRegistrationField Model

**Location**: `backend/apps/academics/models.py`

Allows institutions to define custom fields for student registration dynamically.

**Fields**:
- `field_name` (CharField): Unique identifier (e.g., "aadhar_number")
- `field_label` (CharField): Display label (e.g., "Aadhar Number")
- `field_type` (CharField): Type of input (text, number, date, dropdown, email, phone)
- `dropdown_options` (TextField): Comma-separated options for dropdown fields
- `is_required` (BooleanField): Whether the field is mandatory
- `placeholder` (CharField): Placeholder text for the input
- `help_text` (CharField): Help text to guide users
- `order` (PositiveIntegerField): Display order
- `is_active` (BooleanField): Whether the field is currently active

**Example**:
```python
CustomRegistrationField.objects.create(
    field_name='aadhar_number',
    field_label='Aadhar Number',
    field_type='text',
    is_required=True,
    placeholder='1234-5678-9012',
    help_text='Enter your 12-digit Aadhar number',
    order=1
)
```

---

### 2. Program Model

**Location**: `backend/apps/academics/models.py`

Replaces hardcoded courses with dynamic programs that can be configured per institution.

**Fields**:
- `name` (CharField): Full program name (e.g., "Bachelor of Technology")
- `code` (CharField): Short code (e.g., "BTECH")
- `department` (ForeignKey): Department offering the program
- `duration_years` (PositiveIntegerField): Duration in years
- `duration_semesters` (PositiveIntegerField): Duration in semesters (auto-calculated)
- `total_credits` (PositiveIntegerField): Total credits required
- `description` (TextField): Program description
- `is_active` (BooleanField): Whether accepting students

**Example**:
```python
Program.objects.create(
    name='Bachelor of Technology',
    code='BTECH',
    department=cs_dept,
    duration_years=4,
    total_credits=160,
    description='4-year undergraduate program in Computer Science'
)
```

---

### 3. Enhanced StudentProfile Model

**Location**: `backend/apps/users/models.py`

Updated to support multi-tenant architecture with custom data storage.

**Core Universal Fields** (same for all institutions):
- `reg_no` (CharField): Unique registration number
- `enrollment_number` (CharField): Enrollment number (alias for reg_no)
- `dob` (DateField): Date of birth
- `gender` (CharField): Gender (M/F/O/N)
- `phone` (CharField): Contact phone number
- `address` (TextField): Residential address

**Multi-Tenant Fields**:
- `program` (ForeignKey): Link to Program model
- `custom_data` (JSONField): Stores institution-specific field values

**custom_data Structure**:
```json
{
  "aadhar_number": "1234-5678-9012",
  "samagra_id": "ABC123456",
  "blood_group": "O+",
  "parent_phone": "+91-9876543210",
  "previous_school": "XYZ High School"
}
```

---

## 📡 API Endpoints

### CustomRegistrationField Endpoints

**Base URL**: `/api/academics/custom-fields/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/academics/custom-fields/` | List all custom fields |
| GET | `/api/academics/custom-fields/active_fields/` | Get only active fields |
| GET | `/api/academics/custom-fields/{id}/` | Get specific field |
| POST | `/api/academics/custom-fields/` | Create new field |
| PUT | `/api/academics/custom-fields/{id}/` | Update field |
| PATCH | `/api/academics/custom-fields/{id}/` | Partial update |
| DELETE | `/api/academics/custom-fields/{id}/` | Delete field |

**Query Parameters**:
- `show_inactive=true`: Include inactive fields
- `field_type=text`: Filter by field type
- `is_required=true`: Filter by required status

**Example Response**:
```json
[
  {
    "id": 1,
    "field_name": "aadhar_number",
    "field_label": "Aadhar Number",
    "field_type": "text",
    "dropdown_options": null,
    "dropdown_options_list": [],
    "is_required": true,
    "placeholder": "1234-5678-9012",
    "help_text": "Enter your 12-digit Aadhar number",
    "order": 1,
    "is_active": true,
    "created_at": "2026-03-24T10:00:00Z",
    "updated_at": "2026-03-24T10:00:00Z"
  }
]
```

---

### Program Endpoints

**Base URL**: `/api/academics/programs/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/academics/programs/` | List all programs |
| GET | `/api/academics/programs/by_department/` | Get programs by department |
| GET | `/api/academics/programs/{id}/` | Get specific program |
| POST | `/api/academics/programs/` | Create new program |
| PUT | `/api/academics/programs/{id}/` | Update program |
| PATCH | `/api/academics/programs/{id}/` | Partial update |
| DELETE | `/api/academics/programs/{id}/` | Delete program |

**Query Parameters**:
- `show_inactive=true`: Include inactive programs
- `department={id}`: Filter by department
- `duration_years={n}`: Filter by duration

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "Bachelor of Technology",
    "code": "BTECH",
    "department": {
      "id": 1,
      "name": "Computer Science",
      "code": "CS"
    },
    "department_id": 1,
    "duration_years": 4,
    "duration_semesters": 8,
    "total_credits": 160,
    "description": "4-year undergraduate program",
    "is_active": true,
    "total_students": 150,
    "created_at": "2026-03-24T10:00:00Z",
    "updated_at": "2026-03-24T10:00:00Z"
  }
]
```

---

### Student Registration with Custom Data

**Endpoint**: `POST /api/students/register/` (to be implemented)

**Request Body**:
```json
{
  "user": {
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123"
  },
  "profile": {
    "reg_no": "2026CS001",
    "enrollment_number": "2026CS001",
    "dob": "2005-05-15",
    "gender": "M",
    "phone": "+91-9876543210",
    "address": "123 Main St, City, State",
    "program_id": 1,
    "department_id": 1,
    "current_semester": 1,
    "batch_year": 2026,
    "custom_data": {
      "aadhar_number": "1234-5678-9012",
      "samagra_id": "ABC123456",
      "blood_group": "O+",
      "parent_phone": "+91-9876543210",
      "previous_school": "XYZ High School"
    }
  }
}
```

**Response**:
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "STUDENT"
  },
  "reg_no": "2026CS001",
  "enrollment_number": "2026CS001",
  "dob": "2005-05-15",
  "gender": "M",
  "phone": "+91-9876543210",
  "address": "123 Main St, City, State",
  "program": {
    "id": 1,
    "name": "Bachelor of Technology",
    "code": "BTECH",
    "duration_years": 4,
    "duration_semesters": 8
  },
  "department": {
    "id": 1,
    "name": "Computer Science",
    "code": "CS"
  },
  "current_semester": 1,
  "batch_year": 2026,
  "custom_data": {
    "aadhar_number": "1234-5678-9012",
    "samagra_id": "ABC123456",
    "blood_group": "O+",
    "parent_phone": "+91-9876543210",
    "previous_school": "XYZ High School"
  },
  "created_at": "2026-03-24T10:00:00Z",
  "updated_at": "2026-03-24T10:00:00Z"
}
```

---

## 🔄 Migration Guide

### Step 1: Run Migrations

```bash
cd backend
python manage.py migrate
```

### Step 2: Create Custom Fields

```python
from apps.academics.models import CustomRegistrationField

# Aadhar Number
CustomRegistrationField.objects.create(
    field_name='aadhar_number',
    field_label='Aadhar Number',
    field_type='text',
    is_required=True,
    placeholder='1234-5678-9012',
    help_text='Enter your 12-digit Aadhar number',
    order=1
)

# Samagra ID
CustomRegistrationField.objects.create(
    field_name='samagra_id',
    field_label='Samagra ID',
    field_type='text',
    is_required=False,
    placeholder='ABC123456',
    help_text='Enter your Samagra ID if applicable',
    order=2
)

# Blood Group
CustomRegistrationField.objects.create(
    field_name='blood_group',
    field_label='Blood Group',
    field_type='dropdown',
    dropdown_options='A+,A-,B+,B-,AB+,AB-,O+,O-',
    is_required=False,
    order=3
)
```

### Step 3: Create Programs

```python
from apps.academics.models import Program, Department

cs_dept = Department.objects.get(code='CS')

# B.Tech Program
Program.objects.create(
    name='Bachelor of Technology',
    code='BTECH',
    department=cs_dept,
    duration_years=4,
    total_credits=160,
    description='4-year undergraduate program in Computer Science'
)

# M.Tech Program
Program.objects.create(
    name='Master of Technology',
    code='MTECH',
    department=cs_dept,
    duration_years=2,
    total_credits=80,
    description='2-year postgraduate program in Computer Science'
)
```

### Step 4: Update Existing Students (Optional)

```python
from apps.users.models import StudentProfile

# Migrate existing students to use reg_no
for student in StudentProfile.objects.all():
    if not student.reg_no:
        student.reg_no = student.enrollment_number
        student.save()
```

---

## 🎨 Frontend Integration

### Fetching Custom Fields

```javascript
// Fetch active custom fields for registration form
const response = await api.get('/api/academics/custom-fields/active_fields/');
const customFields = response.data;

// Render dynamic form fields
customFields.forEach(field => {
  switch (field.field_type) {
    case 'text':
      renderTextInput(field);
      break;
    case 'number':
      renderNumberInput(field);
      break;
    case 'date':
      renderDateInput(field);
      break;
    case 'dropdown':
      renderDropdown(field, field.dropdown_options_list);
      break;
    case 'email':
      renderEmailInput(field);
      break;
    case 'phone':
      renderPhoneInput(field);
      break;
  }
});
```

### Submitting Registration with Custom Data

```javascript
const registrationData = {
  user: {
    username: formData.username,
    email: formData.email,
    first_name: formData.firstName,
    last_name: formData.lastName,
    password: formData.password
  },
  profile: {
    reg_no: formData.regNo,
    enrollment_number: formData.regNo,
    dob: formData.dob,
    gender: formData.gender,
    phone: formData.phone,
    address: formData.address,
    program_id: formData.programId,
    department_id: formData.departmentId,
    current_semester: 1,
    batch_year: new Date().getFullYear(),
    custom_data: {
      // Dynamically collected custom field values
      aadhar_number: formData.aadharNumber,
      samagra_id: formData.samagraId,
      blood_group: formData.bloodGroup,
      // ... other custom fields
    }
  }
};

await api.post('/api/students/register/', registrationData);
```

---

## 🔒 Security Considerations

1. **Validation**: Custom data is validated as a JSON object
2. **Sanitization**: All custom field values should be sanitized on the frontend
3. **Access Control**: Only admins can create/modify custom fields
4. **Data Privacy**: Custom data may contain sensitive information (Aadhar, etc.)
5. **Audit Logging**: Track changes to custom fields and programs

---

## 📊 Database Schema

### CustomRegistrationField Table
```sql
CREATE TABLE academics_customregistrationfield (
    id BIGINT PRIMARY KEY,
    field_name VARCHAR(100) UNIQUE NOT NULL,
    field_label VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) NOT NULL,
    dropdown_options TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    placeholder VARCHAR(200),
    help_text VARCHAR(200),
    order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Program Table
```sql
CREATE TABLE academics_program (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    department_id BIGINT REFERENCES academics_department(id),
    duration_years INTEGER NOT NULL,
    duration_semesters INTEGER NOT NULL,
    total_credits INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### StudentProfile Table (Updated)
```sql
ALTER TABLE users_studentprofile
ADD COLUMN reg_no VARCHAR(50) UNIQUE,
ADD COLUMN dob DATE,
ADD COLUMN gender VARCHAR(1),
ADD COLUMN phone VARCHAR(15),
ADD COLUMN address TEXT,
ADD COLUMN program_id BIGINT REFERENCES academics_program(id),
ADD COLUMN custom_data JSONB DEFAULT '{}';
```

---

## 🎯 Benefits

1. **Flexibility**: Institutions can add custom fields without code changes
2. **Scalability**: Supports multiple institutions with different requirements
3. **Maintainability**: Centralized configuration reduces code complexity
4. **User Experience**: Dynamic forms adapt to institution needs
5. **Data Integrity**: JSONField ensures structured custom data storage

---

## 🚀 Next Steps

1. **Frontend Implementation**: Build dynamic registration form
2. **Admin UI**: Create interface for managing custom fields and programs
3. **Validation Rules**: Add custom validation for specific field types
4. **Data Migration**: Migrate existing data to new structure
5. **Testing**: Comprehensive tests for multi-tenant features
6. **Documentation**: API documentation for custom endpoints

---

## 📝 Example Use Cases

### Use Case 1: Indian College (Aadhar, Samagra ID)
```python
# Custom fields for Indian institution
fields = [
    {'field_name': 'aadhar_number', 'field_label': 'Aadhar Number', 'is_required': True},
    {'field_name': 'samagra_id', 'field_label': 'Samagra ID', 'is_required': False},
    {'field_name': 'caste_category', 'field_type': 'dropdown', 'dropdown_options': 'General,OBC,SC,ST'}
]
```

### Use Case 2: International University (Passport, Visa)
```python
# Custom fields for international institution
fields = [
    {'field_name': 'passport_number', 'field_label': 'Passport Number', 'is_required': True},
    {'field_name': 'visa_type', 'field_label': 'Visa Type', 'is_required': True},
    {'field_name': 'country_of_origin', 'field_label': 'Country', 'is_required': True}
]
```

### Use Case 3: Medical College (Medical History)
```python
# Custom fields for medical institution
fields = [
    {'field_name': 'blood_group', 'field_type': 'dropdown', 'dropdown_options': 'A+,A-,B+,B-,AB+,AB-,O+,O-'},
    {'field_name': 'allergies', 'field_label': 'Known Allergies', 'field_type': 'text'},
    {'field_name': 'emergency_contact', 'field_label': 'Emergency Contact', 'field_type': 'phone'}
]
```

---

*Last Updated: March 24, 2026*
*Version: 2.0.0 - Multi-Tenant Architecture*
