-- Create the database
CREATE DATABASE academic_erp;
USE academic_erp;

-- 1. Departments Table
CREATE TABLE Departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    dept_code VARCHAR(10) NOT NULL UNIQUE
);

-- 2. Users Table (Base for Students, Faculty, and Admin)
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE, -- University Roll No for Students
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('Student', 'Faculty', 'Admin') NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Student Profiles (Step 1 of Registration)
CREATE TABLE Student_Profiles (
    student_id INT PRIMARY KEY,
    dob DATE,
    home_address TEXT,
    parent_name VARCHAR(100),
    parent_contact VARCHAR(15),
    family_income DECIMAL(12, 2),
    category VARCHAR(20),
    aadhar_no VARCHAR(12) UNIQUE,
    abc_id VARCHAR(20) UNIQUE,
    bank_name VARCHAR(100),
    bank_account_no VARCHAR(20),
    hostel_name VARCHAR(50),
    room_no VARCHAR(10),
    scholarship_eligible BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 4. Faculty Profiles
CREATE TABLE Faculty_Profiles (
    faculty_id INT PRIMARY KEY,
    designation VARCHAR(50),
    dept_id INT,
    specialization VARCHAR(100),
    FOREIGN KEY (faculty_id) REFERENCES Users(user_id),
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
);

-- 5. Courses Table
CREATE TABLE Courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(10) UNIQUE,
    course_name VARCHAR(100),
    credits INT DEFAULT 4,
    dept_id INT,
    syllabus_url VARCHAR(255),
    is_mandatory BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
);

-- 6. Course-Faculty Assignment (Admin Tool)
CREATE TABLE Faculty_Assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    faculty_id INT,
    semester_no INT,
    academic_year VARCHAR(10),
    section VARCHAR(5),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (faculty_id) REFERENCES Faculty_Profiles(faculty_id)
);

-- 7. Student Registration & Enrollments (Step 2 of Registration)
CREATE TABLE Enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    course_id INT,
    semester_no INT,
    is_backlog BOOLEAN DEFAULT FALSE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Verified', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- 8. Attendance Management (Faculty Module)
CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    assignment_id INT,
    student_id INT,
    attendance_date DATE,
    status ENUM('Present', 'Absent', 'Late') DEFAULT 'Present',
    FOREIGN KEY (assignment_id) REFERENCES Faculty_Assignments(assignment_id),
    FOREIGN KEY (student_id) REFERENCES Users(user_id)
);

-- 9. Grade Management (Step 3 of Faculty Module)
CREATE TABLE Grades (
    grade_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    course_id INT,
    quiz_marks DECIMAL(5,2),
    midterm_marks DECIMAL(5,2),
    assignment_marks DECIMAL(5,2),
    final_exam_marks DECIMAL(5,2),
    total_gpa DECIMAL(3,2),
    is_published BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- 10. Fee Payments (Step 3 of Registration)
CREATE TABLE Fee_Payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    academic_fees DECIMAL(10, 2),
    hostel_fees DECIMAL(10, 2),
    mess_fees DECIMAL(10, 2),
    scholarship_deduction DECIMAL(10, 2) DEFAULT 0.00,
    total_paid DECIMAL(10, 2),
    payment_status ENUM('Successful', 'Failed', 'Pending') DEFAULT 'Pending',
    transaction_id VARCHAR(100) UNIQUE,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Users(user_id)
);

-- 11. Anonymous Feedback (Student Module)
CREATE TABLE Faculty_Feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    faculty_id INT,
    criteria_1_score INT, -- Content Quality
    criteria_2_score INT, -- Explanation
    -- ... and so on for 10 criteria
    additional_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (faculty_id) REFERENCES Faculty_Profiles(faculty_id)
);

-- 12. Notices Table
CREATE TABLE Notices (
    notice_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    content TEXT,
    target_role ENUM('All', 'Student', 'Faculty') DEFAULT 'All',
    is_pinned BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);