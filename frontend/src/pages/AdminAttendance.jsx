import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminAttendance.css';

const AdminAttendance = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedReport, setSelectedReport] = useState(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [attendanceData, setAttendanceData] = useState([]);
  const [loadingAttendance, setLoadingAttendance] = useState(false);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewNotes, setReviewNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch all attendance report submissions
  const fetchReports = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/attendance/admin/reports/');
      setReports(response.data.reports || []);
    } catch (err) {
      console.error('Error fetching reports:', err);
      setError('Failed to load attendance reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // Toast helpers
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Fetch attendance details for a report
  const viewReportDetails = async (report) => {
    setSelectedReport(report);
    setIsViewModalOpen(true);
    setLoadingAttendance(true);

    try {
      // Extract just the year from batch_string (e.g., "2024-IMG" -> "2024")
      const batchYear = report.batch_string.split('-')[0];
      
      console.log('Fetching attendance for:', {
        subject_id: report.subject.id,
        batch: batchYear,
        full_batch_string: report.batch_string
      });

      // Fetch attendance summary for this subject and batch
      const response = await api.get('/api/faculty/attendance-summary/', {
        params: {
          subject_id: report.subject.id,
          batch: batchYear
        }
      });

      console.log('Attendance response:', response.data);

      if (response.data.subjects && response.data.subjects.length > 0) {
        const subjectData = response.data.subjects[0];
        console.log('Subject data:', subjectData);
        console.log('Batches:', subjectData.batches);
        
        // The backend returns batches keyed by year only (e.g., "2024")
        // So we should look for the batch using the extracted year
        const batchData = subjectData.batches[batchYear];
        
        console.log('Batch data for year', batchYear, ':', batchData);
        
        if (batchData && batchData.students) {
          setAttendanceData(batchData.students);
        } else {
          // If no exact match, try to get all students from all batches
          console.log('No exact batch match, collecting all students');
          const allStudents = [];
          Object.values(subjectData.batches).forEach(batch => {
            if (batch.students) {
              allStudents.push(...batch.students);
            }
          });
          setAttendanceData(allStudents);
        }
      } else {
        console.log('No subjects found in response');
        setAttendanceData([]);
      }
    } catch (err) {
      console.error('Error fetching attendance details:', err);
      console.error('Error response:', err.response?.data);
      showToast('Failed to load attendance details.', 'error');
      setAttendanceData([]);
    } finally {
      setLoadingAttendance(false);
    }
  };

  // Open review modal
  const openReviewModal = (report, action) => {
    setSelectedReport({ ...report, reviewAction: action });
    setReviewNotes('');
    setIsReviewModalOpen(true);
  };

  // Submit review (approve or reject)
  const submitReview = async () => {
    if (!selectedReport) return;

    setIsSubmitting(true);
    try {
      await api.patch('/api/attendance/admin/reports/', {
        report_id: selectedReport.id,
        action: selectedReport.reviewAction,
        notes: reviewNotes
      });

      showToast(
        `Report ${selectedReport.reviewAction}d successfully!`,
        'success'
      );
      setIsReviewModalOpen(false);
      setIsViewModalOpen(false);
      await fetchReports();
    } catch (err) {
      console.error('Error reviewing report:', err);
      showToast('Failed to submit review.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get status badge class
  const getStatusBadge = (status) => {
    const badges = {
      pending: 'status-badge pending',
      approved: 'status-badge approved',
      rejected: 'status-badge rejected'
    };
    return badges[status] || 'status-badge';
  };

  // Get status text
  const getStatusText = (status) => {
    const texts = {
      pending: 'Pending Review',
      approved: 'Approved',
      rejected: 'Rejected'
    };
    return texts[status] || status;
  };

  if (loading) {
    return <Loader message="Loading attendance reports..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchReports} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="admin-attendance">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="attendance-header">
        <h1>📋 Attendance Reports</h1>
        <p>Review and approve faculty attendance submissions</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-cards">
        <div className="stat-card pending-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>{reports.filter(r => r.status === 'pending').length}</h3>
            <p>Pending Review</p>
          </div>
        </div>
        <div className="stat-card approved-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{reports.filter(r => r.status === 'approved').length}</h3>
            <p>Approved</p>
          </div>
        </div>
        <div className="stat-card rejected-card">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <h3>{reports.filter(r => r.status === 'rejected').length}</h3>
            <p>Rejected</p>
          </div>
        </div>
      </div>

      {/* Reports Table */}
      <div className="reports-section">
        <h2>All Submissions</h2>
        {reports.length > 0 ? (
          <div className="table-container">
            <table className="reports-table">
              <thead>
                <tr>
                  <th>Faculty</th>
                  <th>Subject</th>
                  <th>Batch</th>
                  <th>Submitted</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>
                      <div className="faculty-info">
                        <div className="faculty-name">{report.faculty.name}</div>
                        <div className="faculty-id">{report.faculty.employee_id}</div>
                      </div>
                    </td>
                    <td>
                      <div className="subject-info">
                        <div className="subject-name">{report.subject.name}</div>
                        <div className="subject-code">{report.subject.code}</div>
                      </div>
                    </td>
                    <td className="batch-cell">{report.batch_string}</td>
                    <td className="date-cell">
                      {new Date(report.submitted_at).toLocaleDateString()}
                    </td>
                    <td>
                      <span className={getStatusBadge(report.status)}>
                        {getStatusText(report.status)}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button
                        className="action-btn view-btn"
                        onClick={() => viewReportDetails(report)}
                      >
                        View
                      </button>
                      {report.status === 'pending' && (
                        <>
                          <button
                            className="action-btn approve-btn"
                            onClick={() => openReviewModal(report, 'approve')}
                          >
                            Approve
                          </button>
                          <button
                            className="action-btn reject-btn"
                            onClick={() => openReviewModal(report, 'reject')}
                          >
                            Reject
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No attendance reports submitted yet</p>
          </div>
        )}
      </div>

      {/* View Report Details Modal */}
      <Modal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        title={`Attendance Report - ${selectedReport?.subject.name}`}
      >
        {loadingAttendance ? (
          <div className="modal-loading">
            <Loader message="Loading attendance data..." size="medium" />
          </div>
        ) : (
          <div className="report-details">
            <div className="report-info">
              <div className="info-row">
                <span className="info-label">Faculty:</span>
                <span className="info-value">{selectedReport?.faculty.name}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Subject:</span>
                <span className="info-value">{selectedReport?.subject.code} - {selectedReport?.subject.name}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Batch:</span>
                <span className="info-value">{selectedReport?.batch_string}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Status:</span>
                <span className={getStatusBadge(selectedReport?.status)}>
                  {getStatusText(selectedReport?.status)}
                </span>
              </div>
              {selectedReport?.reviewed_by && (
                <>
                  <div className="info-row">
                    <span className="info-label">Reviewed By:</span>
                    <span className="info-value">{selectedReport.reviewed_by}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Reviewed At:</span>
                    <span className="info-value">
                      {new Date(selectedReport.reviewed_at).toLocaleString()}
                    </span>
                  </div>
                  {selectedReport.notes && (
                    <div className="info-row">
                      <span className="info-label">Notes:</span>
                      <span className="info-value">{selectedReport.notes}</span>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="attendance-details">
              <h3>Student Attendance</h3>
              {attendanceData.length > 0 ? (
                <div className="attendance-table-container">
                  <table className="attendance-table">
                    <thead>
                      <tr>
                        <th>Roll No</th>
                        <th>Name</th>
                        <th>Total Classes</th>
                        <th>Attended</th>
                        <th>Percentage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendanceData.map((student) => (
                        <tr key={student.student_id}>
                          <td className="roll-no">{student.reg_no}</td>
                          <td className="student-name">{student.name}</td>
                          <td className="center-text">{student.total_classes}</td>
                          <td className="center-text">{student.attended}</td>
                          <td className="center-text">
                            <span className={`percentage ${student.attendance_percentage >= 75 ? 'good' : 'low'}`}>
                              {student.attendance_percentage}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="no-data">No attendance data available</p>
              )}
            </div>

            {selectedReport?.status === 'pending' && (
              <div className="modal-actions">
                <button
                  className="btn btn-success"
                  onClick={() => openReviewModal(selectedReport, 'approve')}
                >
                  Approve Report
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => openReviewModal(selectedReport, 'reject')}
                >
                  Reject Report
                </button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Review Modal */}
      <Modal
        isOpen={isReviewModalOpen}
        onClose={() => setIsReviewModalOpen(false)}
        title={`${selectedReport?.reviewAction === 'approve' ? 'Approve' : 'Reject'} Report`}
      >
        <div className="review-modal">
          <div className="review-info">
            <p>
              You are about to <strong>{selectedReport?.reviewAction}</strong> the attendance report for:
            </p>
            <ul>
              <li><strong>Faculty:</strong> {selectedReport?.faculty.name}</li>
              <li><strong>Subject:</strong> {selectedReport?.subject.name}</li>
              <li><strong>Batch:</strong> {selectedReport?.batch_string}</li>
            </ul>
            {selectedReport?.reviewAction === 'approve' && (
              <p className="warning-text">
                Once approved, the faculty will not be able to edit this attendance anymore.
              </p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="review-notes">Notes (Optional)</label>
            <textarea
              id="review-notes"
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="Add any comments or feedback..."
              rows="4"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setIsReviewModalOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="button"
              className={`btn ${selectedReport?.reviewAction === 'approve' ? 'btn-success' : 'btn-danger'}`}
              onClick={submitReview}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : `${selectedReport?.reviewAction === 'approve' ? 'Approve' : 'Reject'}`}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AdminAttendance;
