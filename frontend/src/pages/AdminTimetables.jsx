import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminTimetables.css';

const AdminTimetables = () => {
  const [loading, setLoading] = useState(true);
  const [timetables, setTimetables] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    academic_year: '',
    semester: '',
    department: '',
    pdf_file: null,
    notes: '',
    is_active: true
  });

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch timetables and departments
  useEffect(() => {
    fetchTimetables();
    fetchDepartments();
  }, []);

  const fetchTimetables = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/academics/timetables/pdfs/');
      setTimetables(response.data);
    } catch (err) {
      console.error('Error fetching timetables:', err);
      showToast('Failed to load timetables', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/api/academics/departments/');
      setDepartments(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching departments:', err);
    }
  };

  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setFormData(prev => ({ ...prev, pdf_file: file }));
    } else {
      showToast('Please select a valid PDF file', 'error');
      e.target.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.title || !formData.academic_year || !formData.pdf_file) {
      showToast('Please fill in all required fields', 'warning');
      return;
    }

    try {
      setUploading(true);

      const submitData = new FormData();
      submitData.append('title', formData.title);
      submitData.append('academic_year', formData.academic_year);
      if (formData.semester) submitData.append('semester', formData.semester);
      if (formData.department) submitData.append('department', formData.department);
      if (formData.notes) submitData.append('notes', formData.notes);
      submitData.append('is_active', formData.is_active);
      submitData.append('pdf_file', formData.pdf_file);

      await api.post('/api/academics/timetables/upload/', submitData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      showToast('Timetable uploaded successfully!', 'success');
      setShowUploadForm(false);
      setFormData({
        title: '',
        academic_year: '',
        semester: '',
        department: '',
        pdf_file: null,
        notes: '',
        is_active: true
      });
      fetchTimetables();
    } catch (err) {
      console.error('Error uploading timetable:', err);
      showToast(err.response?.data?.error || 'Failed to upload timetable', 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this timetable?')) {
      return;
    }

    try {
      await api.delete(`/api/academics/timetables/pdfs/${id}/`);
      showToast('Timetable deleted successfully', 'success');
      fetchTimetables();
    } catch (err) {
      console.error('Error deleting timetable:', err);
      showToast('Failed to delete timetable', 'error');
    }
  };

  if (loading) {
    return <Loader message="Loading timetables..." size="large" />;
  }

  return (
    <div className="admin-timetables">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      <div className="page-header">
        <div>
          <h1>📅 Timetable Management</h1>
          <p>Upload and manage timetable PDFs for students and faculty</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowUploadForm(!showUploadForm)}
        >
          {showUploadForm ? '✕ Cancel' : '+ Upload Timetable'}
        </button>
      </div>

      {showUploadForm && (
        <div className="upload-form-card">
          <h2>Upload New Timetable</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="e.g., Fall 2024 Timetable"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="academic_year">Academic Year *</label>
                <input
                  type="text"
                  id="academic_year"
                  name="academic_year"
                  value={formData.academic_year}
                  onChange={handleInputChange}
                  placeholder="e.g., 2024-25"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="semester">Semester (Optional)</label>
                <input
                  type="number"
                  id="semester"
                  name="semester"
                  value={formData.semester}
                  onChange={handleInputChange}
                  placeholder="e.g., 1, 2, 3..."
                  min="1"
                  max="10"
                />
              </div>

              <div className="form-group">
                <label htmlFor="department">Department (Optional)</label>
                <select
                  id="department"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                >
                  <option value="">All Departments</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="pdf_file">PDF File *</label>
              <input
                type="file"
                id="pdf_file"
                name="pdf_file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
              <small>Upload a PDF file (max 7-8 pages recommended)</small>
            </div>

            <div className="form-group">
              <label htmlFor="notes">Notes (Optional)</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Additional notes or instructions..."
                rows="3"
              />
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="form-checkbox"
                />
                <span className="checkbox-text">Make timetable visible to students and faculty</span>
              </label>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn-submit"
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload Timetable'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="timetables-list">
        <h2>Uploaded Timetables</h2>
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
                    <small>Uploaded by {timetable.uploaded_by_name || 'Admin'}</small>
                    <small>{new Date(timetable.created_at).toLocaleDateString()}</small>
                  </div>
                </div>
                <div className="card-actions">
                  <a
                    href={timetable.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-view"
                  >
                    👁️ View PDF
                  </a>
                  <button
                    onClick={() => handleDelete(timetable.id)}
                    className="btn-delete"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📅</div>
            <p>No timetables uploaded yet</p>
            <p className="empty-subtext">Click "Upload Timetable" to add a new timetable PDF</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminTimetables;
