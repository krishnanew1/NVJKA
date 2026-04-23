import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './StudentTimetable.css';

const FacultyTimetable = () => {
  const [loading, setLoading] = useState(true);
  const [pdfs, setPdfs] = useState([]);
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState('');
  const [facultyProfile, setFacultyProfile] = useState(null);

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
      const profileRes = await api.get('/api/users/dashboard/faculty/');
      setFacultyProfile(profileRes.data);
      const facultyId = profileRes.data?.id;

      const [pdfRes, entriesRes] = await Promise.all([
        api.get('/api/academics/timetables/pdfs/').catch(() => ({ data: [] })),
        facultyId
          ? api.get('/api/academics/timetables/', { params: { faculty_id: facultyId, is_active: true } }).catch(() => ({ data: [] }))
          : Promise.resolve({ data: [] }),
      ]);

      setPdfs(pdfRes.data || []);
      const eData = entriesRes.data?.results || entriesRes.data || [];
      setEntries(Array.isArray(eData) ? eData : []);
    } catch (err) {
      console.error('Error fetching timetables:', err);
      if (err.response?.status === 404) {
        setPdfs([]);
        setEntries([]);
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

  const dayOrder = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
  const grouped = entries.reduce((acc, e) => {
    const day = e.day_of_week || 'UNKNOWN';
    if (!acc[day]) acc[day] = [];
    acc[day].push(e);
    return acc;
  }, {});
  dayOrder.forEach(d => {
    if (grouped[d]) {
      grouped[d] = grouped[d].slice().sort((a, b) => String(a.start_time).localeCompare(String(b.start_time)));
    }
  });

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

      {/* Structured timetable entries */}
      {entries.length > 0 ? (
        <div className="timetables-grid" style={{ gridTemplateColumns: '1fr' }}>
          {dayOrder.filter(d => grouped[d] && grouped[d].length > 0).map(day => (
            <div key={day} className="timetable-card">
              <div className="card-header">
                <div className="header-left">
                  <div className="card-icon">🗓️</div>
                  <h3 className="card-title">{day}</h3>
                </div>
                <div className="card-badge">{grouped[day].length} classes</div>
              </div>
              <div className="card-body">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {grouped[day].map(e => (
                    <div key={e.id} className="detail-item" style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                      <div>
                        <div style={{ fontWeight: 700 }}>
                          {e.start_time} - {e.end_time} • {e.subject?.code} ({e.class_name})
                        </div>
                        <div style={{ opacity: 0.85 }}>
                          {e.subject?.name} • {e.classroom || e.room_number || '—'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', opacity: 0.8 }}>
                        <div>{e.academic_year}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">🗓️</div>
          <p>No structured timetable entries yet</p>
          <p className="empty-subtext">If your admin uploads entries, they will show here.</p>
        </div>
      )}

      {/* PDF fallback */}
      <div className="page-header" style={{ marginTop: 18 }}>
        <h2 style={{ margin: 0 }}>📄 Timetable PDFs</h2>
        <p style={{ marginTop: 6 }}>Optional PDF schedules uploaded by the administration</p>
      </div>

      {pdfs.length > 0 ? (
        <div className="timetables-grid">
          {pdfs.map(timetable => (
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
          <div className="empty-icon">📄</div>
          <p>No timetable PDFs available</p>
        </div>
      )}
    </div>
  );
};

export default FacultyTimetable;
