import { useEffect, useState } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const FacultyWorks = () => {
  const [loading, setLoading] = useState(true);
  const [works, setWorks] = useState([]);
  const [error, setError] = useState('');

  const [toast, setToast] = useState({ isVisible: false, message: '', type: 'info' });
  const showToast = (message, type = 'info') => setToast({ isVisible: true, message, type });
  const hideToast = () => setToast(prev => ({ ...prev, isVisible: false }));

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState({
    kind: 'PAPER',
    title: '',
    description: '',
    external_url: '',
    is_public: true,
    file: null,
  });

  const fetchWorks = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get('/api/users/faculty/works/');
      setWorks(res.data || []);
    } catch (err) {
      console.error(err);
      setError('Failed to load your works. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorks();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ kind: 'PAPER', title: '', description: '', external_url: '', is_public: true, file: null });
    setIsModalOpen(true);
  };

  const openEdit = (work) => {
    setEditing(work);
    setForm({
      kind: work.kind || 'PAPER',
      title: work.title || '',
      description: work.description || '',
      external_url: work.external_url || '',
      is_public: !!work.is_public,
      file: null,
    });
    setIsModalOpen(true);
  };

  const saveWork = async (e) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      const fd = new FormData();
      fd.append('kind', form.kind);
      fd.append('title', form.title);
      fd.append('description', form.description || '');
      fd.append('external_url', form.external_url || '');
      fd.append('is_public', String(form.is_public));
      if (form.file) fd.append('file', form.file);

      if (editing) {
        await api.patch(`/api/users/faculty/works/${editing.id}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
        showToast('Work updated.', 'success');
      } else {
        await api.post('/api/users/faculty/works/', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
        showToast('Work added.', 'success');
      }

      setIsModalOpen(false);
      await fetchWorks();
    } catch (err) {
      console.error(err);
      showToast('Failed to save work.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const deleteWork = async (work) => {
    if (!window.confirm('Delete this work?')) return;
    try {
      await api.delete(`/api/users/faculty/works/${work.id}/`);
      showToast('Deleted.', 'success');
      await fetchWorks();
    } catch (err) {
      console.error(err);
      showToast('Failed to delete.', 'error');
    }
  };

  if (loading) return <Loader message="Loading your works..." size="large" />;

  return (
    <div className="dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="page-header">
        <h1>🧾 My Research & Works</h1>
        <p>Add papers, projects, and other works to your profile</p>
      </div>

      {error && (
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <p className="error-text">{error}</p>
          <button onClick={fetchWorks} className="retry-button">Retry</button>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
        <button className="primary-btn" onClick={openCreate}>+ Add work</button>
      </div>

      {works.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <p>No works added yet</p>
          <p className="empty-subtext">Add your research papers or projects so students can view them.</p>
        </div>
      ) : (
        <div className="cards-grid">
          {works.map(w => (
            <div key={w.id} className="dashboard-card">
              <div className="card-header">
                <h3 className="card-title">{w.title}</h3>
                <span className="card-badge">{w.kind}</span>
              </div>
              <div className="card-body">
                <p className="card-description">{w.description || '—'}</p>
                <div className="card-meta">
                  <small>{w.is_public ? 'Public' : 'Private'}</small>
                  <small>Updated {new Date(w.updated_at).toLocaleDateString()}</small>
                </div>
                <div style={{ marginTop: 8, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  {w.external_url && <a href={w.external_url} target="_blank" rel="noreferrer">Open link</a>}
                  {w.file_url && <a href={w.file_url} target="_blank" rel="noreferrer">Download file</a>}
                </div>
              </div>
              <div className="card-actions">
                <button className="secondary-btn" onClick={() => openEdit(w)}>Edit</button>
                <button className="danger-btn" onClick={() => deleteWork(w)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => (isSaving ? null : setIsModalOpen(false))}
        title={editing ? 'Edit work' : 'Add work'}
      >
        <form onSubmit={saveWork} className="form">
          <div className="form-group">
            <label>Kind</label>
            <select value={form.kind} onChange={(e) => setForm(prev => ({ ...prev, kind: e.target.value }))}>
              <option value="PAPER">Research Paper</option>
              <option value="PROJECT">Project</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Title</label>
            <input value={form.title} onChange={(e) => setForm(prev => ({ ...prev, title: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea value={form.description} onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))} rows={4} />
          </div>
          <div className="form-group">
            <label>External URL (optional)</label>
            <input value={form.external_url} onChange={(e) => setForm(prev => ({ ...prev, external_url: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>File (optional)</label>
            <input type="file" onChange={(e) => setForm(prev => ({ ...prev, file: e.target.files?.[0] || null }))} />
          </div>
          <div className="form-row">
            <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input type="checkbox" checked={form.is_public} onChange={(e) => setForm(prev => ({ ...prev, is_public: e.target.checked }))} />
              Public (visible to students)
            </label>
          </div>
          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={() => setIsModalOpen(false)} disabled={isSaving}>Cancel</button>
            <button type="submit" className="primary-btn" disabled={isSaving}>
              {isSaving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default FacultyWorks;

