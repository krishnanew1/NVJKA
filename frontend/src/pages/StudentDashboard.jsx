import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
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

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSubjectDetails, setSelectedSubjectDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

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
        api.get('/api/users/student/dashboard/').catch(() => null),
        api.get('/api/students/semester-register/').catch(() => ({ data: [] })),
        api.get('/api/attendance/my-records/').catch(() => ({ data: { attendance: [] } }))
      ]);

      // Set student profile
      if (profileResponse && profileResponse.data) {
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

  // Fetch detailed attendance records for a subject
  const fetchAttendanceDetails = async (subjectId) => {
    try {
      setLoadingDetails(true);
      
      const response = await api.get('/api/attendance/my-records/', {
        params: { details: 'true' }
      });

      const attendanceInfo = response.data || {};
      const allAttendance = attendanceInfo.attendance || [];
      
      // Find the specific subject's details
      const subjectDetails = allAttendance.find(item => item.subject.id === subjectId);
      
      if (subjectDetails) {
        setSelectedSubjectDetails(subjectDetails);
        setIsModalOpen(true);
      } else {
        showToast('No attendance details found for this subject', 'warning');
      }
    } catch (err) {
      console.error('Error fetching attendance details:', err);
      showToast('Failed to load attendance details', 'error');
    } finally {
      setLoadingDetails(false);
    }
  };

  // Handle view details button click
  const handleViewDetails = (subjectId) => {
    fetchAttendanceDetails(subjectId);
  };

  // Close modal
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedSubjectDetails(null);
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
  };

  // Get status color class
  const getStatusColorClass = (status) => {
    switch (status) {
      case 'Present':
        return 'status-present';
      case 'Absent':
        return 'status-absent';
      case 'Late':
        return 'status-late';
      default:
        return '';
    }
  };

  // Get attendance percentage color
  const getAttendanceColor = (percentage) => {
    if (percentage >= 75) return 'success';
    if (percentage >= 60) return 'warning';
    return 'danger';
  };

  // Get attendance status text
  const getAttendanceStatus = (percentage) => {
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
  const enrollmentNumber = studentProfile?.enrollment_number || 'N/A';
  const currentSemester = studentProfile?.current_semester || 'N/A';
  const departmentName = studentProfile?.department?.name || 'N/A';

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
                <span className="detail-value">{enrollmentNumber}</span>
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

      {/* Attendance Overview Section */}
      {attendanceData.length > 0 && (
        <div className="attendance-section">
          <div className="section-header">
            <h2>📊 Attendance Overview</h2>
            <p>Your attendance across all subjects</p>
          </div>

          <div className="attendance-grid">
            {attendanceData.map((record) => (
              <div key={record.subject.id} className="attendance-card">
                <div className="attendance-card-header">
                  <h3 className="attendance-subject-name">{record.subject.name}</h3>
                  <span className="attendance-subject-code">{record.subject.code}</span>
                </div>
                <div className="attendance-card-body">
                  <div className="attendance-stats">
                    <div className="stat-item">
                      <span className="stat-label">Total Classes</span>
                      <span className="stat-value">{record.total_classes}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Present</span>
                      <span className="stat-value success">{record.present}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Absent</span>
                      <span className="stat-value danger">{record.absent}</span>
                    </div>
                    {record.late > 0 && (
                      <div className="stat-item">
                        <span className="stat-label">Late</span>
                        <span className="stat-value warning">{record.late}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="attendance-progress">
                    <div className="progress-header">
                      <span className="progress-label">Attendance</span>
                      <span className={`progress-percentage ${getAttendanceColor(record.percentage)}`}>
                        {record.percentage}%
                      </span>
                    </div>
                    <div className="progress-bar-container">
                      <div 
                        className={`progress-bar ${getAttendanceColor(record.percentage)}`}
                        style={{ width: `${record.percentage}%` }}
                      ></div>
                    </div>
                    <div className="progress-status">
                      <span className={`status-badge ${getAttendanceColor(record.percentage)}`}>
                        {getAttendanceStatus(record.percentage)}
                      </span>
                      {record.percentage < 75 && (
                        <span className="status-warning">
                          ⚠️ Below required 75%
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* View Details Button */}
                  <button
                    className="view-details-btn"
                    onClick={() => handleViewDetails(record.subject.id)}
                    disabled={loadingDetails}
                  >
                    {loadingDetails ? 'Loading...' : '📋 View Details'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state for attendance */}
      {attendanceData.length === 0 && enrollments.length > 0 && (
        <div className="attendance-section">
          <div className="section-header">
            <h2>📊 Attendance Overview</h2>
            <p>Your attendance across all subjects</p>
          </div>
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No attendance records found</p>
            <p className="empty-subtext">Attendance will appear here once your faculty marks it</p>
          </div>
        </div>
      )}

      {/* Attendance Details Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={selectedSubjectDetails ? `Attendance Details - ${selectedSubjectDetails.subject.name}` : 'Attendance Details'}
      >
        {selectedSubjectDetails && (
          <div className="attendance-details-modal">
            {/* Subject Info Header */}
            <div className="modal-subject-header">
              <div className="modal-subject-info">
                <h3>{selectedSubjectDetails.subject.name}</h3>
                <span className="modal-subject-code">{selectedSubjectDetails.subject.code}</span>
              </div>
              <div className="modal-subject-stats">
                <div className="modal-stat">
                  <span className="modal-stat-label">Attendance</span>
                  <span className={`modal-stat-value ${getAttendanceColor(selectedSubjectDetails.percentage)}`}>
                    {selectedSubjectDetails.percentage}%
                  </span>
                </div>
                <div className="modal-stat">
                  <span className="modal-stat-label">Total Classes</span>
                  <span className="modal-stat-value">{selectedSubjectDetails.total_classes}</span>
                </div>
              </div>
            </div>

            {/* Attendance Records Table */}
            {selectedSubjectDetails.records && selectedSubjectDetails.records.length > 0 ? (
              <div className="attendance-details-table-container">
                <table className="attendance-details-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Recorded By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedSubjectDetails.records.map((record, index) => (
                      <tr key={index}>
                        <td className="detail-date">{formatDate(record.date)}</td>
                        <td>
                          <span className={`detail-status ${getStatusColorClass(record.status)}`}>
                            {record.status === 'Present' && '✓ '}
                            {record.status === 'Absent' && '✗ '}
                            {record.status === 'Late' && '⏰ '}
                            {record.status}
                          </span>
                        </td>
                        <td className="detail-recorded-by">{record.recorded_by}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="modal-empty-state">
                <div className="modal-empty-icon">📋</div>
                <p>No attendance records found for this subject</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StudentDashboard;