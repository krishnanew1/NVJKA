import { useEffect, useState } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentFaculty = () => {
  const [loading, setLoading] = useState(true);
  const [faculty, setFaculty] = useState([]);
  const [error, setError] = useState('');

  const [toast, setToast] = useState({ isVisible: false, message: '', type: 'info' });
  const showToast = (message, type = 'info') => setToast({ isVisible: true, message, type });
  const hideToast = () => setToast(prev => ({ ...prev, isVisible: false }));

  const [selected, setSelected] = useState(null);
  const [works, setWorks] = useState([]);
  const [worksLoading, setWorksLoading] = useState(false);
  const [isWorksOpen, setIsWorksOpen] = useState(false);

  const fetchFaculty = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get('/api/users/faculty/');
      const data = res.data?.results || res.data || [];
      setFaculty(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError('Failed to load faculty directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFaculty();
  }, []);

  const openWorks = async (f) => {
    setSelected(f);
    setIsWorksOpen(true);
    setWorksLoading(true);
    setWorks([]);
    try {
      const res = await api.get(`/api/users/faculty/${f.id}/works/`);
      setWorks(res.data || []);
    } catch (err) {
      console.error(err);
      showToast('Failed to load faculty works.', 'error');
    } finally {
      setWorksLoading(false);
    }
  };

  if (loading) return <Loader message="Loading faculty..." size="large" />;

  return (
    <div className="dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="page-header">
        <h1>👨‍🏫 Faculty</h1>
        <p>View faculty profiles and their research/works</p>
      </div>

      {error && (
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <p className="error-text">{error}</p>
          <button onClick={fetchFaculty} className="retry-button">Retry</button>
        </div>
      )}

      {faculty.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">👤</div>
          <p>No faculty found</p>
        </div>
      ) : (
        <div className="cards-grid">
          {faculty.map(f => (
            <div key={f.id} className="dashboard-card">
              <div className="card-header">
                <h3 className="card-title">{f.user?.full_name || f.user?.username}</h3>
                <span className="card-badge">{f.designation || 'Faculty'}</span>
              </div>
              <div className="card-body">
                <p className="card-description">{f.specialization || '—'}</p>
                <div className="card-meta">
                  <small>{f.department?.name || '—'}</small>
                </div>
              </div>
              <div className="card-actions">
                <button className="secondary-btn" onClick={() => openWorks(f)}>View works</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={isWorksOpen} onClose={() => setIsWorksOpen(false)} title="Faculty works">
        {worksLoading ? (
          <Loader message="Loading works..." />
        ) : works.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📄</div>
            <p>No public works available</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {works.map(w => (
              <div key={w.id} className="dashboard-card" style={{ padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{w.title}</div>
                    <div style={{ fontSize: 12, opacity: 0.8 }}>{w.kind}</div>
                  </div>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                    {w.external_url && <a href={w.external_url} target="_blank" rel="noreferrer">Open link</a>}
                    {w.file_url && <a href={w.file_url} target="_blank" rel="noreferrer">Download</a>}
                  </div>
                </div>
                {w.description && <div style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>{w.description}</div>}
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StudentFaculty;

