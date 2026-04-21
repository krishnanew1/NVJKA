import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentDashboard = () => {
  // State management
  const [studentProfile, setStudentProfile] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch student data
  const fetchStudentData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch student profile, semester registrations, and attendance in parallel
      const [profileResponse, semesterRegResponse, attendanceResponse] = await Promise.all([
        api.get('/api/users/dashboard/student/').catch(() => null),
        api.get('/api/students/semester-register/').catch(() => ({ data: [] })),
        api.get('/api/attendance/my-records/').catch(() => ({ data: { attendance: [] } }))
      ]);

      
      // Set student profile
      if (profileResponse && profileResponse.data) {
        console.log("Student Profile Data:", profileResponse.data);
        setStudentProfile(profileResponse.data);
      }

      // Extract registered subjects from semester registrations
      const semesterRegData = semesterRegResponse.data.results || semesterRegResponse.data || [];
      const registeredSubjects = [];
      
      // Flatten all registered courses from all semester registrations
      semesterRegData.forEach(registration => {
        if (registration.registered_courses && registration.registered_courses.length > 0) {
          registration.registered_courses.forEach(course => {
            if (course.subject) {
              registeredSubjects.push({
                id: course.id,
                subject: course.subject,
                is_backlog: course.is_backlog,
                semester: registration.semester,
                academic_year: registration.academic_year,
                status: 'Active' // You can adjust this based on your logic
              });
            }
          });
        }
      });

      setEnrollments(registeredSubjects);

      // Set attendance data
      const attendanceInfo = attendanceResponse.data || {};
      setAttendanceData(attendanceInfo.attendance || []);

    } catch (err) {
      console.error('Error fetching student data:', err);
      
      // Handle 404 as empty state, not an error
      if (err.response?.status === 404) {
        setEnrollments([]);
        setAttendanceData([]);
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Student privileges required.');
      } else {
        setError('Failed to load student data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentData();
  }, []);

  // Toast helper functions
  const showToast = (message, type = 'info') => {
    setToast({
      isVisible: true,
      message,
      type
    });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Get attendance percentage color (updated thresholds)
  const getAttendanceColor = (percentage) => {
    if (percentage >= 90) return 'success';
    if (percentage >= 75) return 'warning';
    return 'danger';
  };

  // Calculate overall attendance percentage
  const calculateOverallAttendance = () => {
    if (attendanceData.length === 0) return 0;
    
    let totalClasses = 0;
    let totalPresent = 0;
    
    attendanceData.forEach(record => {
      totalClasses += record.total_classes;
      totalPresent += record.present + record.late; // Count late as present
    });
    
    return totalClasses > 0 ? Math.round((totalPresent / totalClasses) * 100) : 0;
  };

  // Get attendance status text
  const getAttendanceStatus = (percentage) => {
    if (percentage >= 90) return 'Excellent';
    if (percentage >= 75) return 'Good';
    if (percentage >= 60) return 'Average';
    return 'Low';
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <Loader message="Loading your dashboard..." size="large" />
  );

  // Error message component
  const ErrorMessage = () => (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{error}</p>
      <button 
        onClick={() => window.location.reload()} 
        className="retry-button"
      >
        Retry
      </button>
    </div>
  );

  // Show loading state
  if (loading) return <LoadingSpinner />;
  
  // Show error state
  if (error) return <ErrorMessage />;

  // Get user info from localStorage as fallback
  const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
  const studentName = studentProfile?.user?.full_name || 
                      `${userInfo.first_name || ''} ${userInfo.last_name || ''}`.trim() || 
                      userInfo.username || 
                      'Student';
  const rollNumber = studentProfile?.roll_number || studentProfile?.enrollment_number || 'N/A';
  const currentSemester = studentProfile?.current_semester || 'N/A';
  const departmentName = studentProfile?.department?.name || 'N/A';
  const overallAttendance = calculateOverallAttendance();

  return (
    <div className="student-dashboard">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Hero Section - Welcome Banner */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-icon">👨‍🎓</div>
          <div className="hero-text">
            <h1 className="hero-title">Welcome, {studentName}!</h1>
            <div className="hero-details">
              <span className="hero-detail">
                <span className="detail-label">Roll No:</span>
                <span className="detail-value">{rollNumber}</span>
              </span>
              <span className="hero-divider">•</span>
              <span className="hero-detail">
                <span className="detail-label">Semester:</span>
                <span className="detail-value">{currentSemester}</span>
              </span>
              <span className="hero-divider">•</span>
              <span className="hero-detail">
                <span className="detail-label">Department:</span>
                <span className="detail-value">{departmentName}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Enrolled Subjects Section */}
      <div className="subjects-section">
        <div className="section-header">
          <h2>📚 My Enrolled Subjects</h2>
          <p>Subjects you are currently taking</p>
        </div>

        {enrollments.length > 0 ? (
          <div className="subjects-grid">
            {enrollments.map((enrollment) => (
              <div key={enrollment.id} className="subject-card">
                <div className="subject-card-header">
                  <div className="subject-icon">📖</div>
                  <div className="subject-badge">
                    {enrollment.subject?.code || 'N/A'}
                  </div>
                </div>
                <div className="subject-card-body">
                  <h3 className="subject-name">
                    {enrollment.subject?.name || 'Subject Name'}
                  </h3>
                  <p className="subject-code">
                    {enrollment.subject?.credits ? `${enrollment.subject.credits} Credits` : 'N/A'}
                  </p>
                  <div className="subject-info">
                    <span className="info-item">
                      <span className="info-icon">📅</span>
                      {enrollment.semester || 'N/A'}
                    </span>
                    <span className="info-item">
                      <span className="info-icon">📊</span>
                      {enrollment.is_backlog ? 'Backlog' : enrollment.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <p>You are not enrolled in any subjects yet</p>
            <p className="empty-subtext">Please complete your semester registration to enroll in subjects</p>
          </div>
        )}
      </div>

      {/* Attendance Overview Section - Minimalist Widget */}
      {attendanceData.length > 0 && (
        <div className="attendance-section">
          <div className="section-header">
            <h2>📊 Attendance Overview</h2>
            <p>Your overall attendance performance</p>
          </div>

          <div className="attendance-widget">
            <div className="attendance-widget-content">
              <div className="attendance-circle">
                <svg className="attendance-progress-ring" width="200" height="200">
                  <circle
                    className="attendance-progress-ring-circle-bg"
                    stroke="#e0e0e0"
                    strokeWidth="20"
                    fill="transparent"
                    r="80"
                    cx="100"
                    cy="100"
                  />
                  <circle
                    className={`attendance-progress-ring-circle ${getAttendanceColor(overallAttendance)}`}
                    stroke="currentColor"
                    strokeWidth="20"
                    fill="transparent"
                    r="80"
                    cx="100"
                    cy="100"
                    strokeDasharray={`${(overallAttendance / 100) * 502.4} 502.4`}
                    strokeDashoffset="0"
                    transform="rotate(-90 100 100)"
                  />
                </svg>
                <div className="attendance-percentage-display">
                  <span className={`attendance-percentage-value ${getAttendanceColor(overallAttendance)}`}>
                    {overallAttendance}%
                  </span>
                  <span className="attendance-percentage-label">Overall</span>
                </div>
              </div>
              <div className="attendance-widget-info">
                <h3 className="attendance-widget-title">Overall Attendance</h3>
                <p className="attendance-widget-description">
                  {overallAttendance >= 90 && '🎉 Excellent! Keep up the great work!'}
                  {overallAttendance >= 75 && overallAttendance < 90 && '👍 Good attendance. Stay consistent!'}
                  {overallAttendance < 75 && '⚠️ Below required 75%. Please improve!'}
                </p>
                <Link to="/student/attendance" className="view-details-btn-primary">
                  📋 View Detailed Attendance
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty state for attendance */}
      {attendanceData.length === 0 && enrollments.length > 0 && (
        <div className="attendance-section">
          <div className="section-header">
            <h2>📊 Attendance Overview</h2>
            <p>Your overall attendance performance</p>
          </div>
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No attendance records found</p>
            <p className="empty-subtext">Attendance will appear here once your faculty marks it</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;