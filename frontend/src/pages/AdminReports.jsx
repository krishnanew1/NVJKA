import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import Modal from '../components/Modal';
import './AdminReports.css';

const AdminReports = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, reviewed: 0 });
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, pending, reviewed

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch reports
  const fetchReports = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/attendance/admin/reports/');
      
      setReports(response.data.reports || []);
      setStats({
        total: response.data.total || 0,
        pending: response.data.pending || 0,
        reviewed: response.data.reviewed || 0
      });
    } catch (err) {
      console.error('Error fetching reports:', err);
      
      if (err.response?.status === 403) {
        setError('Access denied. Admin privileges required.');
      } else {
        setError('Failed to load reports. Please try again.');
      }
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

  // Handle review report
  const handleReviewClick = (report) => {
    setSelectedReport(report);
    setReviewNotes(report.notes || '');
    setIsModalOpen(true);
  };

  const handleSubmitReview = async () => {
    if (!selectedReport) return;

    try {
      setSubmitting(true);

      await api.patch('/api/attendance/admin/reports/', {
        report_id: selectedReport.id,
        notes: reviewNotes
      });

      showToast('Report reviewed successfully!', 'success');
      setIsModalOpen(false);
      setSelectedReport(null);
      setReviewNotes('');
      
      // Refresh reports
      fetchReports();
    } catch (err) {
      console.error('Error reviewing report:', err);
      showToast('Failed to review report. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  // Filter reports
  const filteredReports = reports.filter(report => {
    if (filter === 'pending') return !report.is_reviewed;
    if (filter === 'reviewed') return report.is_reviewed;
    return true;
  });

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <Loader message="Loading reports..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon"></div>
        <p className="error-text">{error}</p>
        <button onClick={fetchReports} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="admin-reports">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="reports-header">
        <h1>Attendance Reports</h1>
        <p>Review and manage attendance reports submitted by faculty</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"></div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.total}</h3>
            <p className="stat-label">Total Reports</p>
          </div>
        </div>
        <div className="stat-card pending-card">
          <div className="stat-icon"></div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.pending}</h3>
            <p className="stat-label">Pending Review</p>
          </div>
        </div>
        <div className="stat-card reviewed-card">
          <div className="stat-icon"></div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.reviewed}</h3>
            <p className="stat-label">Reviewed</p>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        <button
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Reports ({stats.total})
        </button>
        <button
          className={`filter-tab ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          Pending ({stats.pending})
        </button>
        <button
          className={`filter-tab ${filter === 'reviewed' ? 'active' : ''}`}
          onClick={() => setFilter('reviewed')}
        >
          Reviewed ({stats.reviewed})
        </button>
      </div>

      {/* Reports Table */}
      {filteredReports.length > 0 ? (
        <div className="reports-table-container">
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
              {filteredReports.map((report) => (
                <tr key={report.id}>
                  <td className="faculty-cell">
                    <div className="faculty-info">
                      <span className="faculty-name">{report.faculty.name}</span>
                      <span className="faculty-id">{report.faculty.employee_id}</span>
                    </div>
                  </td>
                  <td className="subject-cell">
                    <div className="subject-info">
                      <span className="subject-name">{report.subject.name}</span>
                      <span className="subject-code">{report.subject.code}</span>
                    </div>
                  </td>
                  <td className="batch-cell">{report.batch_string}</td>
                  <td className="date-cell">{formatDate(report.submitted_at)}</td>
                  <td className="status-cell">
                    {report.is_reviewed ? (
                      <span className="status-badge reviewed">
                        Reviewed
                      </span>
                    ) : (
                      <span className="status-badge pending">
                        Pending
                      </span>
                    )}
                  </td>
                  <td className="actions-cell">
                    <button
                      className="review-btn"
                      onClick={() => handleReviewClick(report)}
                    >
                      {report.is_reviewed ? 'View' : 'Review'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p>No {filter !== 'all' ? filter : ''} reports found</p>
          <p className="empty-subtext">
            {filter === 'pending' 
              ? 'All reports have been reviewed' 
              : 'Reports will appear here once faculty submit them'}
          </p>
        </div>
      )}

      {/* Review Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedReport(null);
          setReviewNotes('');
        }}
        title="Review Attendance Report"
      >
        {selectedReport && (
          <div className="review-modal-content">
            <div className="report-details">
              <div className="detail-row">
                <span className="detail-label">Faculty:</span>
                <span className="detail-value">{selectedReport.faculty.name}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Subject:</span>
                <span className="detail-value">
                  {selectedReport.subject.name} ({selectedReport.subject.code})
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Batch:</span>
                <span className="detail-value">{selectedReport.batch_string}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Submitted:</span>
                <span className="detail-value">{formatDate(selectedReport.submitted_at)}</span>
              </div>
              {selectedReport.is_reviewed && (
                <>
                  <div className="detail-row">
                    <span className="detail-label">Reviewed By:</span>
                    <span className="detail-value">{selectedReport.reviewed_by}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Reviewed At:</span>
                    <span className="detail-value">{formatDate(selectedReport.reviewed_at)}</span>
                  </div>
                </>
              )}
            </div>

            <div className="notes-section">
              <label htmlFor="review-notes">Review Notes:</label>
              <textarea
                id="review-notes"
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Add notes about this report..."
                rows="4"
                disabled={selectedReport.is_reviewed}
              />
            </div>

            {!selectedReport.is_reviewed && (
              <div className="modal-actions">
                <button
                  className="submit-review-btn"
                  onClick={handleSubmitReview}
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Mark as Reviewed'}
                </button>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AdminReports;
