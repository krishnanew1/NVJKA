import { useEffect, useMemo, useState } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const FacultyAssignments = () => {
  const [loading, setLoading] = useState(true);
  const [assignments, setAssignments] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [error, setError] = useState('');

  const [toast, setToast] = useState({ isVisible: false, message: '', type: 'info' });
  const showToast = (message, type = 'info') => setToast({ isVisible: true, message, type });
  const hideToast = () => setToast(prev => ({ ...prev, isVisible: false }));

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    subjectId: '',
    batchYear: '',
    semester: '',
    title: '',
    description: '',
    dueAt: '',
    requiresSubmission: true,
    allowLate: false,
    attachment: null,
  });

  const [selected, setSelected] = useState(null);
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [submissions, setSubmissions] = useState([]);

  const subjectById = useMemo(() => {
    const map = new Map();
    subjects.forEach(s => map.set(String(s.id), s));
    return map;
  }, [subjects]);

  const fetchAll = async () => {
    try {
      setLoading(true);
      setError('');

      const [aRes, sRes] = await Promise.all([
        api.get('/api/assignments/'),
        api.get('/api/academics/faculty/my-subjects/'),
      ]);

      const aData = aRes.data?.results || aRes.data || [];
      const sData = sRes.data?.results || sRes.data || [];
      setAssignments(Array.isArray(aData) ? aData : []);
      setSubjects(Array.isArray(sData) ? sData : []);
    } catch (err) {
      console.error(err);
      setError('Failed to load assignments. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const openCreate = () => {
    setCreateForm({
      subjectId: '',
      batchYear: '',
      semester: '',
      title: '',
      description: '',
      dueAt: '',
      requiresSubmission: true,
      allowLate: false,
      attachment: null,
    });
    setIsCreateOpen(true);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const subject = subjectById.get(String(createForm.subjectId));
      const departmentId = subject?.course?.department?.id || subject?.course?.department_id;
      if (!departmentId) {
        showToast('Could not determine department for this subject.', 'error');
        return;
      }

      const form = new FormData();
      form.append('subject', createForm.subjectId);
      form.append('department', String(departmentId));
      form.append('batch_year', createForm.batchYear);
      form.append('semester', createForm.semester);
      form.append('title', createForm.title);
      form.append('description', createForm.description || '');
      if (createForm.dueAt) form.append('due_at', createForm.dueAt);
      form.append('requires_submission', String(createForm.requiresSubmission));
      form.append('allow_late', String(createForm.allowLate));
      if (createForm.attachment) form.append('attachment', createForm.attachment);

      await api.post('/api/assignments/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      showToast('Assignment created.', 'success');
      setIsCreateOpen(false);
      await fetchAll();
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.detail || 'Failed to create assignment.', 'error');
    }
  };

  const openSubmissions = async (assignment) => {
    setSelected(assignment);
    setIsSubmissionsOpen(true);
    setSubmissionsLoading(true);
    setSubmissions([]);

    try {
      const res = await api.get(`/api/assignments/${assignment.id}/submissions/`);
      setSubmissions(res.data || []);
    } catch (err) {
      console.error(err);
      showToast('Failed to load submissions.', 'error');
    } finally {
      setSubmissionsLoading(false);
    }
  };

  if (loading) return <Loader message="Loading assignments..." size="large" />;

  return (
    <div className="dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="page-header">
        <h1>📚 Assignments</h1>
        <p>Create assignments for a batch and review submissions</p>
      </div>

      {error && (
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <p className="error-text">{error}</p>
          <button onClick={fetchAll} className="retry-button">Retry</button>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
        <button className="primary-btn" onClick={openCreate}>+ New Assignment</button>
      </div>

      {assignments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <p>No assignments created yet</p>
          <p className="empty-subtext">Create an assignment for a subject and batch.</p>
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
                <button className="secondary-btn" onClick={() => openSubmissions(a)}>View submissions</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create assignment">
        <form onSubmit={handleCreate} className="form">
          <div className="form-group">
            <label>Subject</label>
            <select
              value={createForm.subjectId}
              onChange={(e) => {
                const subjectId = e.target.value;
                const subj = subjectById.get(String(subjectId));
                setCreateForm(prev => ({
                  ...prev,
                  subjectId,
                  semester: subj?.semester ? String(subj.semester) : prev.semester,
                }));
              }}
              required
            >
              <option value="">Select subject</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>
                  {s.code} - {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Batch year</label>
              <input
                type="number"
                value={createForm.batchYear}
                onChange={(e) => setCreateForm(prev => ({ ...prev, batchYear: e.target.value }))}
                placeholder="e.g. 2026"
                required
              />
            </div>
            <div className="form-group">
              <label>Semester</label>
              <input
                type="number"
                value={createForm.semester}
                onChange={(e) => setCreateForm(prev => ({ ...prev, semester: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Title</label>
            <input
              value={createForm.title}
              onChange={(e) => setCreateForm(prev => ({ ...prev, title: e.target.value }))}
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={createForm.description}
              onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
              rows={4}
            />
          </div>

          <div className="form-group">
            <label>Due at (optional)</label>
            <input
              type="datetime-local"
              value={createForm.dueAt}
              onChange={(e) => setCreateForm(prev => ({ ...prev, dueAt: e.target.value }))}
            />
          </div>

          <div className="form-row">
            <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={createForm.requiresSubmission}
                onChange={(e) => setCreateForm(prev => ({ ...prev, requiresSubmission: e.target.checked }))}
              />
              Requires submission
            </label>
            <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={createForm.allowLate}
                onChange={(e) => setCreateForm(prev => ({ ...prev, allowLate: e.target.checked }))}
              />
              Allow late submissions
            </label>
          </div>

          <div className="form-group">
            <label>Attachment (optional)</label>
            <input type="file" onChange={(e) => setCreateForm(prev => ({ ...prev, attachment: e.target.files?.[0] || null }))} />
          </div>

          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={() => setIsCreateOpen(false)}>Cancel</button>
            <button type="submit" className="primary-btn">Create</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={isSubmissionsOpen} onClose={() => setIsSubmissionsOpen(false)} title="Submissions">
        {submissionsLoading ? (
          <Loader message="Loading submissions..." />
        ) : submissions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No submissions yet</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {submissions.map(s => (
              <div key={s.id} className="dashboard-card" style={{ padding: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{s.student?.full_name || s.student?.username}</div>
                    <div style={{ fontSize: 12, opacity: 0.8 }}>
                      {s.submitted_at ? `Submitted ${new Date(s.submitted_at).toLocaleString()}` : 'Not submitted'}
                      {s.is_late ? ' (Late)' : ''}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                    {s.file_url && (
                      <a href={s.file_url} target="_blank" rel="noreferrer">Download</a>
                    )}
                  </div>
                </div>
                {s.text_answer && (
                  <div style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>{s.text_answer}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default FacultyAssignments;

