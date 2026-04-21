import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './StudentTimetable.css';

const FacultyTimetable = () => {
  const [loading, setLoading] = useState(true);
  const [timetables, setTimetables] = useState([]);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  useEffect(() => {
    fetchTimetables();
  }, []);

  const fetchTimetables = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/academics/timetables/pdfs/');
      setTimetables(response.data);
    } catch (err) {
      console.error('Error fetching timetables:', err);
      if (err.response?.status === 404) {
        setTimetables([]);
      } else {
        setError('Failed to load timetables. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  if (loading) {
    return <Loader message="Loading timetables..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchTimetables} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="student-timetable">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      <div className="page-header">
        <h1>📅 My Timetable</h1>
        <p>View your teaching schedule and timetable</p>
      </div>

      {timetables.length > 0 ? (
        <div className="timetables-grid">
          {timetables.map(timetable => (
            <div key={timetable.id} className="timetable-card">
              <div className="card-header">
                <div className="header-left">
                  <div className="card-icon">📄</div>
                  <h3 className="card-title">{timetable.title}</h3>
                </div>
                <div className="card-badge">{timetable.academic_year}</div>
              </div>
              <div className="card-body">
                <div className="card-details">
                  {timetable.semester && (
                    <span className="detail-item">
                      📚 Semester {timetable.semester}
                    </span>
                  )}
                  {timetable.department_name && (
                    <span className="detail-item">
                      🏛️ {timetable.department_name}
                    </span>
                  )}
                  {!timetable.department_name && (
                    <span className="detail-item">
                      🌐 All Departments
                    </span>
                  )}
                </div>
                {timetable.notes && (
                  <p className="card-notes">{timetable.notes}</p>
                )}
                <div className="card-meta">
                  <small>Updated {new Date(timetable.updated_at).toLocaleDateString()}</small>
                </div>
              </div>
              <div className="card-actions">
                <a
                  href={timetable.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-view-pdf"
                >
                  👁️ View Timetable PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <p>No timetables available yet</p>
          <p className="empty-subtext">Your timetable will appear here once uploaded by the administration</p>
        </div>
      )}
    </div>
  );
};

export default FacultyTimetable;
