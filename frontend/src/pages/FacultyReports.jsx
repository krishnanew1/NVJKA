import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './FacultyReports.css';

const FacultyReports = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, reviewed: 0 });
  const [error, setError] = useState('');

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

      const response = await api.get('/api/attendance/faculty/reports/');
      
      setReports(response.data.reports || []);
      setStats({
        total: response.data.total || 0,
        pending: response.data.pending || 0,
        reviewed: response.data.reviewed || 0
      });
    } catch (err) {
      console.error('Error fetching reports:', err);
      
      if (err.response?.status === 403) {
        setError('Access denied. Faculty privileges required.');
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
    return <Loader message="Loading your reports..." size="large" />;
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
    <div className="faculty-reports">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="reports-header">
        <h1>My Report Submissions</h1>
        <p>Track your attendance report submissions and their review status</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"></div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.total}</h3>
            <p className="stat-label">Total Submitted</p>
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

      {/* Reports List */}
      {reports.length > 0 ? (
        <div className="reports-list">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-card-header">
                <div className="report-info">
                  <h3 className="report-subject">{report.subject.name}</h3>
                  <span className="report-code">{report.subject.code}</span>
                </div>
                <div className="report-status">
                  {report.is_reviewed ? (
                    <span className="status-badge reviewed">
                      Reviewed
                    </span>
                  ) : (
                    <span className="status-badge pending">
                      Pending
                    </span>
                  )}
                </div>
              </div>

              <div className="report-card-body">
                <div className="report-detail">
                  <span className="detail-label">Batch:</span>
                  <span className="detail-value">{report.batch_string}</span>
                </div>
                <div className="report-detail">
                  <span className="detail-label">Submitted:</span>
                  <span className="detail-value">{formatDate(report.submitted_at)}</span>
                </div>
                {report.is_reviewed && (
                  <>
                    <div className="report-detail">
                      <span className="detail-label">Reviewed By:</span>
                      <span className="detail-value">{report.reviewed_by}</span>
                    </div>
                    <div className="report-detail">
                      <span className="detail-label">Reviewed At:</span>
                      <span className="detail-value">{formatDate(report.reviewed_at)}</span>
                    </div>
                    {report.notes && (
                      <div className="report-notes">
                        <span className="notes-label">Admin Notes:</span>
                        <p className="notes-text">{report.notes}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p>No reports submitted yet</p>
          <p className="empty-subtext">
            Submit attendance reports from the Attendance page to track them here
          </p>
        </div>
      )}
    </div>
  );
};

export default FacultyReports;
