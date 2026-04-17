import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const AdminSettings = () => {
  // State management
  const [programs, setPrograms] = useState([]);
  const [customFields, setCustomFields] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal states
  const [isProgramModalOpen, setIsProgramModalOpen] = useState(false);
  const [isFieldModalOpen, setIsFieldModalOpen] = useState(false);

  // Form states
  const [programForm, setProgramForm] = useState({
    name: '',
    code: '',
    department_id: '',
    duration_years: '',
    total_credits: '',
    description: ''
  });

  const [fieldForm, setFieldForm] = useState({
    field_name: '',
    field_label: '',
    field_type: 'text',
    dropdown_options: '',
    is_required: false,
    placeholder: '',
    help_text: '',
    order: 0
  });

  // Loading states
  const [isProgramSubmitting, setIsProgramSubmitting] = useState(false);
  const [isFieldSubmitting, setIsFieldSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Delete confirmation state
  const [deleteConfirmation, setDeleteConfirmation] = useState({
    isOpen: false,
    type: '', // 'program' or 'field'
    item: null,
    isDeleting: false
  });

  // Fetch all data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [programsRes, fieldsRes, deptsRes] = await Promise.all([
        api.get('/api/academics/programs/'),
        api.get('/api/academics/custom-fields/'),
        api.get('/api/academics/departments/')
      ]);

      setPrograms(programsRes.data.results || programsRes.data);
      setCustomFields(fieldsRes.data.results || fieldsRes.data);
      setDepartments(deptsRes.data.results || deptsRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Toast helpers
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Program handlers
  const handleProgramChange = (e) => {
    const { name, value } = e.target;
    setProgramForm(prev => ({ ...prev, [name]: value }));
  };

  const isProgramFormValid = () => {
    return (
      programForm.name.trim().length > 0 &&
      programForm.code.trim().length > 0 &&
      /^[A-Z0-9_-]+$/i.test(programForm.code.trim()) &&
      programForm.department_id !== '' &&
      programForm.duration_years > 0
    );
  };

  const handleProgramSubmit = async (e) => {
    e.preventDefault();
    if (!isProgramFormValid()) {
      showToast('Please fill all required fields correctly.', 'error');
      return;
    }

    setIsProgramSubmitting(true);
    try {
      const data = {
        ...programForm,
        department_id: parseInt(programForm.department_id),
        duration_years: parseInt(programForm.duration_years),
        total_credits: programForm.total_credits ? parseInt(programForm.total_credits) : null
      };

      await api.post('/api/academics/programs/', data);
      setIsProgramModalOpen(false);
      setProgramForm({ name: '', code: '', department_id: '', duration_years: '', total_credits: '', description: '' });
      await fetchData();
      showToast('Program added successfully!', 'success');
    } catch (err) {
      console.error('Error adding program:', err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Failed to add program.';
      showToast(errorMsg, 'error');
    } finally {
      setIsProgramSubmitting(false);
    }
  };

  // Custom field handlers
  const handleFieldChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFieldForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const isFieldFormValid = () => {
    const isNameValid = fieldForm.field_name.trim().length > 0 && /^[a-z0-9_]+$/i.test(fieldForm.field_name.trim());
    const isLabelValid = fieldForm.field_label.trim().length > 0;
    const isDropdownValid = fieldForm.field_type !== 'dropdown' || fieldForm.dropdown_options.trim().length > 0;
    return isNameValid && isLabelValid && isDropdownValid;
  };

  const handleFieldSubmit = async (e) => {
    e.preventDefault();
    if (!isFieldFormValid()) {
      showToast('Please fill all required fields correctly.', 'error');
      return;
    }

    setIsFieldSubmitting(true);
    try {
      const data = {
        ...fieldForm,
        order: parseInt(fieldForm.order) || 0
      };

      await api.post('/api/academics/custom-fields/', data);
      setIsFieldModalOpen(false);
      setFieldForm({ field_name: '', field_label: '', field_type: 'text', dropdown_options: '', is_required: false, placeholder: '', help_text: '', order: 0 });
      await fetchData();
      showToast('Custom field added successfully!', 'success');
    } catch (err) {
      console.error('Error adding field:', err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Failed to add custom field.';
      showToast(errorMsg, 'error');
    } finally {
      setIsFieldSubmitting(false);
    }
  };

  // Delete handlers
  const handleDeleteClick = (type, item) => {
    setDeleteConfirmation({ isOpen: true, type, item, isDeleting: false });
  };

  const handleDeleteConfirm = async () => {
    const { type, item } = deleteConfirmation;
    setDeleteConfirmation(prev => ({ ...prev, isDeleting: true }));

    try {
      const endpoint = type === 'program'
        ? `/api/academics/programs/${item.id}/`
        : `/api/academics/custom-fields/${item.id}/`;

      await api.delete(endpoint);
      setDeleteConfirmation({ isOpen: false, type: '', item: null, isDeleting: false });
      await fetchData();
      showToast(`${type === 'program' ? 'Program' : 'Custom field'} deleted successfully!`, 'success');
    } catch (err) {
      console.error(`Error deleting ${type}:`, err);
      showToast(`Failed to delete ${type}. It may be in use.`, 'error');
    } finally {
      setDeleteConfirmation(prev => ({ ...prev, isDeleting: false }));
    }
  };

  if (loading) return <Loader message="Loading settings..." size="large" />;
  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{error}</p>
      <button onClick={fetchData} className="retry-button">Retry</button>
    </div>
  );

  return (
    <div className="admin-dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="dashboard-header">
        <h1>⚙️ Institute Settings</h1>
        <p>Manage programs, custom registration fields, and student registration</p>
      </div>

      {/* Two-Section Layout Container */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* TOP SECTION: Programs and Custom Fields */}
        <div className="tables-section">
          {/* Programs Section */}
          <div className="table-card">
            <div className="table-header">
              <h2>Academic Programs</h2>
              <button className="add-btn" onClick={() => setIsProgramModalOpen(true)}>
                + Add Program
              </button>
            </div>
            <div className="table-container">
              {programs.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Name</th>
                      <th>Department</th>
                      <th>Duration</th>
                      <th>Credits</th>
                      <th>Students</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {programs.map((program) => (
                      <tr key={program.id}>
                        <td className="table-code">{program.code}</td>
                        <td className="table-name">{program.name}</td>
                        <td>{program.department?.name || 'N/A'}</td>
                        <td>{program.duration_years} years ({program.duration_semesters} sem)</td>
                        <td>{program.total_credits || 'N/A'}</td>
                        <td>{program.total_students || 0}</td>
                        <td className="table-actions">
                          <button className="action-btn delete-btn" onClick={() => handleDeleteClick('program', program)} title="Delete Program">
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🎓</div>
                  <p>No programs found</p>
                  <button className="add-btn" onClick={() => setIsProgramModalOpen(true)}>
                    Add First Program
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Custom Fields Section */}
          <div className="table-card">
            <div className="table-header">
              <h2>Custom Registration Fields</h2>
              <button className="add-btn" onClick={() => setIsFieldModalOpen(true)}>
                + Add Field
              </button>
            </div>
            <div className="table-container">
              {customFields.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Order</th>
                      <th>Label</th>
                      <th>Type</th>
                      <th>Required</th>
                      <th>Active</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customFields.map((field) => (
                      <tr key={field.id}>
                        <td>{field.order}</td>
                        <td className="table-name">{field.field_label}</td>
                        <td><span className="table-code">{field.field_type}</span></td>
                        <td>{field.is_required ? '✅ Yes' : '❌ No'}</td>
                        <td>{field.is_active ? '✅ Active' : '❌ Inactive'}</td>
                        <td className="table-actions">
                          <button className="action-btn delete-btn" onClick={() => handleDeleteClick('field', field)} title="Delete Field">
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">📝</div>
                  <p>No custom fields found</p>
                  <button className="add-btn" onClick={() => setIsFieldModalOpen(true)}>
                    Add First Field
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* BOTTOM SECTION: Manual Student Registration */}
        <div className="table-card">
          <div className="table-header">
            <h2>👨‍🎓 Manual Student Registration</h2>
            <button className="add-btn" onClick={() => {
              // TODO: Open student registration modal
              showToast('Student registration modal coming soon!', 'info');
            }}>
              + Add Student
            </button>
          </div>
          <div className="table-container">
            <div className="info-section" style={{
              padding: '2rem',
              textAlign: 'center',
              color: 'var(--text-secondary)'
            }}>
              <div style={{
                fontSize: '48px',
                marginBottom: '1rem'
              }}>
                👨‍🎓
              </div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: 'var(--text-color)',
                marginBottom: '0.5rem'
              }}>
                Manual Student Registration
              </h3>
              <p style={{
                fontSize: '14px',
                lineHeight: '1.6',
                maxWidth: '600px',
                margin: '0 auto 1.5rem'
              }}>
                Use this section to manually enter and register a student into the system. 
                You can add student details, assign them to programs, and configure their enrollment information.
              </p>
              <button 
                className="add-btn"
                onClick={() => {
                  // TODO: Open student registration modal
                  showToast('Student registration modal coming soon!', 'info');
                }}
              >
                + Add Student
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Add Program Modal */}
      <Modal isOpen={isProgramModalOpen} onClose={() => setIsProgramModalOpen(false)} title="Add New Program">
        <form onSubmit={handleProgramSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="prog-name">Program Name *</label>
            <input type="text" id="prog-name" name="name" value={programForm.name} onChange={handleProgramChange} required disabled={isProgramSubmitting} placeholder="e.g., Bachelor of Technology" />
          </div>
          <div className="form-group">
            <label htmlFor="prog-code">Program Code *</label>
            <input type="text" id="prog-code" name="code" value={programForm.code} onChange={handleProgramChange} required disabled={isProgramSubmitting} placeholder="e.g., BTECH" maxLength="20" />
          </div>
          <div className="form-group">
            <label htmlFor="prog-dept">Department *</label>
            <select id="prog-dept" name="department_id" value={programForm.department_id} onChange={handleProgramChange} required disabled={isProgramSubmitting}>
              <option value="">Select a department</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>{dept.name} ({dept.code})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="prog-duration">Duration (Years) *</label>
            <input type="number" id="prog-duration" name="duration_years" value={programForm.duration_years} onChange={handleProgramChange} required disabled={isProgramSubmitting} placeholder="e.g., 4" min="1" max="10" />
          </div>
          <div className="form-group">
            <label htmlFor="prog-credits">Total Credits</label>
            <input type="number" id="prog-credits" name="total_credits" value={programForm.total_credits} onChange={handleProgramChange} disabled={isProgramSubmitting} placeholder="e.g., 160" min="1" />
          </div>
          <div className="form-group">
            <label htmlFor="prog-desc">Description</label>
            <input type="text" id="prog-desc" name="description" value={programForm.description} onChange={handleProgramChange} disabled={isProgramSubmitting} placeholder="Optional description" />
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setIsProgramModalOpen(false)} disabled={isProgramSubmitting}>Cancel</button>
            <button type="submit" className={`btn btn-primary ${isProgramSubmitting ? 'btn-loading' : ''}`} disabled={isProgramSubmitting || !isProgramFormValid()}>
              {isProgramSubmitting ? 'Adding...' : 'Add Program'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Custom Field Modal */}
      <Modal isOpen={isFieldModalOpen} onClose={() => setIsFieldModalOpen(false)} title="Add Custom Registration Field">
        <form onSubmit={handleFieldSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="field-name">Field Name (Internal) *</label>
            <input type="text" id="field-name" name="field_name" value={fieldForm.field_name} onChange={handleFieldChange} required disabled={isFieldSubmitting} placeholder="e.g., aadhar_number" />
            <small>Use lowercase letters, numbers, and underscores only</small>
          </div>
          <div className="form-group">
            <label htmlFor="field-label">Field Label (Display) *</label>
            <input type="text" id="field-label" name="field_label" value={fieldForm.field_label} onChange={handleFieldChange} required disabled={isFieldSubmitting} placeholder="e.g., Aadhar Number" />
          </div>
          <div className="form-group">
            <label htmlFor="field-type">Field Type *</label>
            <select id="field-type" name="field_type" value={fieldForm.field_type} onChange={handleFieldChange} required disabled={isFieldSubmitting}>
              <option value="text">Text</option>
              <option value="number">Number</option>
              <option value="date">Date</option>
              <option value="dropdown">Dropdown</option>
              <option value="email">Email</option>
              <option value="phone">Phone</option>
            </select>
          </div>
          {fieldForm.field_type === 'dropdown' && (
            <div className="form-group">
              <label htmlFor="field-options">Dropdown Options *</label>
              <input type="text" id="field-options" name="dropdown_options" value={fieldForm.dropdown_options} onChange={handleFieldChange} required disabled={isFieldSubmitting} placeholder="e.g., BH-1, BH-2, GH" />
              <small>Comma-separated values</small>
            </div>
          )}
          <div className="form-group">
            <label htmlFor="field-placeholder">Placeholder</label>
            <input type="text" id="field-placeholder" name="placeholder" value={fieldForm.placeholder} onChange={handleFieldChange} disabled={isFieldSubmitting} placeholder="e.g., Enter your Aadhar number" />
          </div>
          <div className="form-group">
            <label htmlFor="field-help">Help Text</label>
            <input type="text" id="field-help" name="help_text" value={fieldForm.help_text} onChange={handleFieldChange} disabled={isFieldSubmitting} placeholder="e.g., 12-digit Aadhar number" />
          </div>
          <div className="form-group">
            <label htmlFor="field-order">Display Order</label>
            <input type="number" id="field-order" name="order" value={fieldForm.order} onChange={handleFieldChange} disabled={isFieldSubmitting} placeholder="0" min="0" />
          </div>
          <div className="form-group">
            <label>
              <input type="checkbox" name="is_required" checked={fieldForm.is_required} onChange={handleFieldChange} disabled={isFieldSubmitting} />
              {' '}Required Field
            </label>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setIsFieldModalOpen(false)} disabled={isFieldSubmitting}>Cancel</button>
            <button type="submit" className={`btn btn-primary ${isFieldSubmitting ? 'btn-loading' : ''}`} disabled={isFieldSubmitting || !isFieldFormValid()}>
              {isFieldSubmitting ? 'Adding...' : 'Add Field'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={deleteConfirmation.isOpen} onClose={() => setDeleteConfirmation({ isOpen: false, type: '', item: null, isDeleting: false })} title={`Delete ${deleteConfirmation.type === 'program' ? 'Program' : 'Custom Field'}`}>
        <div className="delete-confirmation">
          <div className="delete-warning">
            <div className="warning-icon">⚠️</div>
            <div className="warning-content">
              <h3>Are you sure?</h3>
              <p>You are about to delete "<strong>{deleteConfirmation.item?.name || deleteConfirmation.item?.field_label}</strong>".</p>
              <p className="warning-text">This action cannot be undone.</p>
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setDeleteConfirmation({ isOpen: false, type: '', item: null, isDeleting: false })} disabled={deleteConfirmation.isDeleting}>Cancel</button>
            <button type="button" className={`btn btn-danger ${deleteConfirmation.isDeleting ? 'btn-loading' : ''}`} onClick={handleDeleteConfirm} disabled={deleteConfirmation.isDeleting}>
              {deleteConfirmation.isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AdminSettings;
