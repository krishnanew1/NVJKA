import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentAttendance = () => {
  // State management
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

  // Fetch attendance data
  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/attendance/my-records/');
      const attendanceInfo = response.data || {};
      setAttendanceData(attendanceInfo.attendance || []);

    } catch (err) {
      console.error('Error fetching attendance data:', err);
      
      if (err.response?.status === 404) {
        setAttendanceData([]);
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Student privileges required.');
      } else {
        setError('Failed to load attendance data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendanceData();
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
    if (percentage >= 90) return 'success';
    if (percentage >= 75) return 'warning';
    return 'danger';
  };

  // Get attendance status text
  const getAttendanceStatus = (percentage) => {
    if (percentage >= 90) return 'Excellent';
    if (percentage >= 75) return 'Good';
    if (percentage >= 60) return 'Average';
    return 'Low';
  };

  // Calculate overall attendance
  const calculateOverallAttendance = () => {
    if (attendanceData.length === 0) return 0;
    
    let totalClasses = 0;
    let totalPresent = 0;
    
    attendanceData.forEach(record => {
      totalClasses += record.total_classes;
      totalPresent += record.present + record.late;
    });
    
    return totalClasses > 0 ? Math.round((totalPresent / totalClasses) * 100) : 0;
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <Loader message="Loading attendance data..." size="large" />
  );

  // Error message component
  const ErrorMessage = () => (
    <div className="error-container">
      <div className="error-icon"></div>
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

  const overallAttendance = calculateOverallAttendance();

  return (
    <div className="student-attendance-page">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <h1 className="page-title">My Attendance</h1>
          <p className="page-subtitle">Detailed attendance records for all your subjects</p>
        </div>
        <div className="overall-attendance-badge">
          <span className="badge-label">Overall Attendance</span>
          <span className={`badge-value ${getAttendanceColor(overallAttendance)}`}>
            {overallAttendance}%
          </span>
        </div>
      </div>

      {/* Attendance Details Grid */}
      {attendanceData.length > 0 ? (
        <div className="attendance-details-grid">
          {attendanceData.map((record) => (
            <div key={record.subject.id} className="attendance-detail-card">
              <div className="attendance-detail-card-header">
                <div className="subject-info">
                  <h3 className="subject-name">{record.subject.name}</h3>
                  <span className="subject-code">{record.subject.code}</span>
                </div>
                <span className={`attendance-badge ${getAttendanceColor(record.percentage)}`}>
                  {record.percentage}%
                </span>
              </div>

              <div className="attendance-detail-card-body">
                {/* Statistics - Inline Text Format */}
                <div className="attendance-stats-inline">
                  <span className="stat-inline">Total Classes: <strong>{record.total_classes}</strong></span>
                  <span className="stat-inline stat-success">Present: <strong>{record.present}</strong></span>
                  <span className="stat-inline stat-danger">Absent: <strong>{record.absent}</strong></span>
                  <span className="stat-inline stat-warning">Late: <strong>{record.late}</strong></span>
                </div>

                {/* Progress Bar */}
                <div className="attendance-progress-section">
                  <div className="progress-header">
                    <span className="progress-label">Attendance Progress</span>
                    <span className={`progress-status ${getAttendanceColor(record.percentage)}`}>
                      {getAttendanceStatus(record.percentage)}
                    </span>
                  </div>
                  <div className="progress-bar-container">
                    <div 
                      className={`progress-bar ${getAttendanceColor(record.percentage)}`}
                      style={{ width: `${record.percentage}%` }}
                    >
                      <span className="progress-bar-label">{record.percentage}%</span>
                    </div>
                  </div>
                  {record.percentage < 75 && (
                    <div className="progress-warning">
                      <span className="warning-icon"></span>
                      <span className="warning-text">
                        Below required 75% - Need {Math.ceil((0.75 * record.total_classes) - (record.present + record.late))} more classes
                      </span>
                    </div>
                  )}
                </div>

                {/* View Details Button */}
                <button
                  className="view-details-btn"
                  onClick={() => handleViewDetails(record.subject.id)}
                  disabled={loadingDetails}
                >
                  {loadingDetails ? 'Loading...' : 'View Individual Records'}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p>No attendance records found</p>
          <p className="empty-subtext">Attendance will appear here once your faculty marks it</p>
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
                            {record.status === 'Present' && ' '}
                            {record.status === 'Absent' && ' '}
                            {record.status === 'Late' && ' '}
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
                <div className="modal-empty-icon"></div>
                <p>No attendance records found for this subject</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StudentAttendance;
