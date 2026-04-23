import { useEffect, useState } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentAssignments = () => {
  const [loading, setLoading] = useState(true);
  const [assignments, setAssignments] = useState([]);
  const [error, setError] = useState('');

  const [toast, setToast] = useState({ isVisible: false, message: '', type: 'info' });
  const showToast = (message, type = 'info') => setToast({ isVisible: true, message, type });
  const hideToast = () => setToast(prev => ({ ...prev, isVisible: false }));

  const [selected, setSelected] = useState(null);
  const [isSubmitOpen, setIsSubmitOpen] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitForm, setSubmitForm] = useState({ file: null, textAnswer: '' });

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get('/api/assignments/');
      const data = res.data?.results || res.data || [];
      setAssignments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError('Failed to load assignments. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);

  const openSubmit = (assignment) => {
    setSelected(assignment);
    setSubmitForm({ file: null, textAnswer: '' });
    setIsSubmitOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selected) return;

    try {
      setSubmitLoading(true);
      const form = new FormData();
      if (submitForm.file) form.append('file', submitForm.file);
      if (submitForm.textAnswer) form.append('text_answer', submitForm.textAnswer);

      await api.post(`/api/assignments/${selected.id}/submit/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      showToast('Submitted successfully.', 'success');
      setIsSubmitOpen(false);
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0] || 'Submission failed.';
      showToast(msg, 'error');
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) return <Loader message="Loading assignments..." size="large" />;

  return (
    <div className="dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="page-header">
        <h1>📚 Assignments</h1>
        <p>View assignments for your batch and submit online</p>
      </div>

      {error && (
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <p className="error-text">{error}</p>
          <button onClick={fetchAssignments} className="retry-button">Retry</button>
        </div>
      )}

      {assignments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <p>No assignments for your batch yet</p>
          <p className="empty-subtext">Check back later.</p>
        </div>
      ) : (
        <div className="cards-grid">
          {assignments.map(a => (
            <div key={a.id} className="dashboard-card">
              <div className="card-header">
                <h3 className="card-title">{a.title}</h3>
                <span className="card-badge">Sem {a.semester}</span>
              </div>
              <div className="card-body">
                <p className="card-description">{a.description || '—'}</p>
                <div className="card-meta">
                  <small>Batch {a.batch_year}</small>
                  {a.due_at && <small>Due {new Date(a.due_at).toLocaleString()}</small>}
                </div>
                {a.attachment_url && (
                  <div style={{ marginTop: 8 }}>
                    <a href={a.attachment_url} target="_blank" rel="noreferrer">View attachment</a>
                  </div>
                )}
              </div>
              <div className="card-actions">
                {a.requires_submission ? (
                  <button className="primary-btn" onClick={() => openSubmit(a)}>Submit</button>
                ) : (
                  <button className="secondary-btn" disabled>Submission not required</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={isSubmitOpen} onClose={() => setIsSubmitOpen(false)} title="Submit assignment">
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>File (optional)</label>
            <input type="file" onChange={(e) => setSubmitForm(prev => ({ ...prev, file: e.target.files?.[0] || null }))} />
          </div>
          <div className="form-group">
            <label>Text answer (optional)</label>
            <textarea
              value={submitForm.textAnswer}
              onChange={(e) => setSubmitForm(prev => ({ ...prev, textAnswer: e.target.value }))}
              rows={6}
              placeholder="If no file, you can submit as text."
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={() => setIsSubmitOpen(false)} disabled={submitLoading}>
              Cancel
            </button>
            <button type="submit" className="primary-btn" disabled={submitLoading}>
              {submitLoading ? 'Submitting…' : 'Submit'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default StudentAssignments;

