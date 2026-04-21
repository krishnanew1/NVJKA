import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const AdminStudents = () => {
  // State management
  const [students, setStudents] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [customFields, setCustomFields] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [studentForm, setStudentForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    reg_no: '',
    dob: '',
    gender: '',
    phone: '',
    address: '',
    program_id: '',
    department_id: '',
    current_semester: '1',
    batch_year: new Date().getFullYear(),
    custom_data: {}
  });

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Grouping state
  const [expandedYears, setExpandedYears] = useState({});
  const [expandedPrograms, setExpandedPrograms] = useState({});

  // Fetch data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [studentsRes, programsRes, fieldsRes, deptsRes] = await Promise.all([
        api.get('/api/users/students/'),
        api.get('/api/academics/programs/'),
        api.get('/api/academics/custom-fields/active_fields/'),
        api.get('/api/academics/departments/')
      ]);

      // Safely extract data, defaulting to empty arrays
      const studentsData = studentsRes.data.results || studentsRes.data || [];
      const programsData = programsRes.data.results || programsRes.data || [];
      const fieldsData = fieldsRes.data.results || fieldsRes.data || [];
      const deptsData = deptsRes.data.results || deptsRes.data || [];

      setStudents(Array.isArray(studentsData) ? studentsData : []);
      setPrograms(Array.isArray(programsData) ? programsData : []);
      setCustomFields(Array.isArray(fieldsData) ? fieldsData : []);
      setDepartments(Array.isArray(deptsData) ? deptsData : []);
      
      // Clear any previous errors on successful fetch
      setError('');
    } catch (err) {
      console.error('Error fetching data:', err);
      // Only set error if there's an actual network/server error
      if (err.response) {
        // Server responded with error status
        setError(`Failed to load data: ${err.response.status} ${err.response.statusText}`);
      } else if (err.request) {
        // Request was made but no response received
        setError('Network error. Please check your connection and try again.');
      } else {
        // Something else happened
        setError('Failed to load data. Please try again.');
      }
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

  // Form handlers
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setStudentForm(prev => ({ ...prev, [name]: value }));
  };

  const handleCustomFieldChange = (fieldName, value) => {
    setStudentForm(prev => ({
      ...prev,
      custom_data: {
        ...prev.custom_data,
        [fieldName]: value
      }
    }));
  };

  const isFormValid = () => {
    return (
      studentForm.username.trim().length > 0 &&
      studentForm.email.trim().length > 0 &&
      studentForm.first_name.trim().length > 0 &&
      studentForm.last_name.trim().length > 0 &&
      studentForm.password.length >= 6 &&
      studentForm.reg_no.trim().length > 0 &&
      studentForm.program_id !== ''
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid()) {
      showToast('Please fill all required fields correctly.', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const data = {
        user: {
          username: studentForm.username,
          email: studentForm.email,
          first_name: studentForm.first_name,
          last_name: studentForm.last_name,
          password: studentForm.password,
          role: 'STUDENT'
        },
        profile: {
          reg_no: studentForm.reg_no,
          enrollment_number: studentForm.reg_no,
          dob: studentForm.dob || null,
          gender: studentForm.gender || null,
          phone: studentForm.phone || null,
          address: studentForm.address || null,
          program_id: parseInt(studentForm.program_id),
          department_id: studentForm.department_id ? parseInt(studentForm.department_id) : null,
          current_semester: parseInt(studentForm.current_semester),
          batch_year: parseInt(studentForm.batch_year),
          custom_data: studentForm.custom_data
        }
      };

      await api.post('/api/users/register/', data);
      setIsAddModalOpen(false);
      resetForm();
      await fetchData();
      showToast('Student added successfully!', 'success');
    } catch (err) {
      console.error('Error adding student:', err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Failed to add student.';
      showToast(errorMsg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setStudentForm({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      reg_no: '',
      dob: '',
      gender: '',
      phone: '',
      address: '',
      program_id: '',
      department_id: '',
      current_semester: '1',
      batch_year: new Date().getFullYear(),
      custom_data: {}
    });
  };

  // Render dynamic field
  const renderCustomField = (field) => {
    const value = studentForm.custom_data[field.field_name] || '';

    switch (field.field_type) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <input
            type={field.field_type}
            value={value}
            onChange={(e) => handleCustomFieldChange(field.field_name, e.target.value)}
            placeholder={field.placeholder || ''}
            required={field.is_required}
            disabled={isSubmitting}
          />
        );
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleCustomFieldChange(field.field_name, e.target.value)}
            placeholder={field.placeholder || ''}
            required={field.is_required}
            disabled={isSubmitting}
          />
        );
      case 'date':
        return (
          <input
            type="date"
            value={value}
            onChange={(e) => handleCustomFieldChange(field.field_name, e.target.value)}
            required={field.is_required}
            disabled={isSubmitting}
          />
        );
      case 'dropdown':
        return (
          <select
            value={value}
            onChange={(e) => handleCustomFieldChange(field.field_name, e.target.value)}
            required={field.is_required}
            disabled={isSubmitting}
          >
            <option value="">Select an option</option>
            {field.dropdown_options_list?.map((option, idx) => (
              <option key={idx} value={option}>{option}</option>
            ))}
          </select>
        );
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleCustomFieldChange(field.field_name, e.target.value)}
            placeholder={field.placeholder || ''}
            required={field.is_required}
            disabled={isSubmitting}
          />
        );
    }
  };

  // Hierarchical grouping: Year -> Program
  const groupStudentsByYearAndProgram = () => {
    const grouped = {};

    students.forEach(student => {
      // Extract year from reg_no (first 4 digits)
      const year = student.reg_no?.substring(0, 4) || 'Unknown';
      const programName = student.program?.name || 'No Program';

      if (!grouped[year]) {
        grouped[year] = {};
      }
      if (!grouped[year][programName]) {
        grouped[year][programName] = [];
      }
      grouped[year][programName].push(student);
    });

    return grouped;
  };

  const toggleYear = (year) => {
    setExpandedYears(prev => ({ ...prev, [year]: !prev[year] }));
  };

  const toggleProgram = (year, program) => {
    const key = `${year}-${program}`;
    setExpandedPrograms(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (loading) return <Loader message="Loading students..." size="large" />;
  if (error) return (
    <div className="error-container">
      <div className="error-icon"></div>
      <p className="error-text">{error}</p>
      <button onClick={fetchData} className="retry-button">Retry</button>
    </div>
  );

  const groupedStudents = groupStudentsByYearAndProgram();
  const years = Object.keys(groupedStudents).sort((a, b) => b.localeCompare(a));

  return (
    <div className="admin-dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="dashboard-header">
        <h1>Student Management</h1>
        <p>Manage student registrations with dynamic fields</p>
      </div>

      <div className="summary-section">
        <div className="summary-card">
          <div className="card-icon"></div>
          <div className="card-content">
            <h3 className="card-number">{students.length}</h3>
            <p className="card-label">Total Students</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon"></div>
          <div className="card-content">
            <h3 className="card-number">{programs.length}</h3>
            <p className="card-label">Active Programs</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon"></div>
          <div className="card-content">
            <h3 className="card-number">{customFields.length}</h3>
            <p className="card-label">Custom Fields</p>
          </div>
        </div>
      </div>

      <div className="tables-section">
        <div className="table-card" style={{ gridColumn: '1 / -1' }}>
          <div className="table-header">
            <h2>Students by Year & Program</h2>
            <button className="add-btn" onClick={() => setIsAddModalOpen(true)}>
              + Add Student
            </button>
          </div>
          <div className="table-container">
            {students.length > 0 ? (
              <div className="hierarchical-list">
                {years.map(year => (
                  <div key={year} className="year-group">
                    <div className="year-header" onClick={() => toggleYear(year)}>
                      <span className="expand-icon">{expandedYears[year] ? '▼' : '▶'}</span>
                      <span className="year-title">Year {year}</span>
                      <span className="year-count">({Object.values(groupedStudents[year]).flat().length} students)</span>
                    </div>
                    {expandedYears[year] && (
                      <div className="year-content">
                        {Object.keys(groupedStudents[year]).sort().map(programName => {
                          const programKey = `${year}-${programName}`;
                          const programStudents = groupedStudents[year][programName];
                          return (
                            <div key={programKey} className="program-group">
                              <div className="program-header" onClick={() => toggleProgram(year, programName)}>
                                <span className="expand-icon">{expandedPrograms[programKey] ? '▼' : '▶'}</span>
                                <span className="program-title">{programName}</span>
                                <span className="program-count">({programStudents.length} students)</span>
                              </div>
                              {expandedPrograms[programKey] && (
                                <div className="program-content">
                                  <table className="data-table">
                                    <thead>
                                      <tr>
                                        <th>Reg No</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Semester</th>
                                        <th>Department</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {programStudents.map(student => (
                                        <tr key={student.id}>
                                          <td className="table-code">{student.reg_no}</td>
                                          <td className="table-name">{student.user?.full_name || student.user?.username}</td>
                                          <td>{student.user?.email}</td>
                                          <td>{student.current_semester}</td>
                                          <td>{student.department?.name || 'N/A'}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon"></div>
                <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>No students found</p>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                  Click "Add Student" to register the first batch!
                </p>
                <button className="add-btn" onClick={() => setIsAddModalOpen(true)}>
                  + Add First Student
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Student Modal */}
      <Modal isOpen={isAddModalOpen} onClose={() => { setIsAddModalOpen(false); resetForm(); }} title="Add New Student">
        <form onSubmit={handleSubmit} className="modal-form">
          <h3 style={{ marginTop: 0, marginBottom: '16px', color: 'var(--text-color)' }}>User Account</h3>
          
          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input type="text" id="username" name="username" value={studentForm.username} onChange={handleInputChange} required disabled={isSubmitting} placeholder="e.g., john_doe" />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input type="email" id="email" name="email" value={studentForm.email} onChange={handleInputChange} required disabled={isSubmitting} placeholder="e.g., john@example.com" />
          </div>
          <div className="form-group">
            <label htmlFor="first_name">First Name *</label>
            <input type="text" id="first_name" name="first_name" value={studentForm.first_name} onChange={handleInputChange} required disabled={isSubmitting} placeholder="e.g., John" />
          </div>
          <div className="form-group">
            <label htmlFor="last_name">Last Name *</label>
            <input type="text" id="last_name" name="last_name" value={studentForm.last_name} onChange={handleInputChange} required disabled={isSubmitting} placeholder="e.g., Doe" />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input type="password" id="password" name="password" value={studentForm.password} onChange={handleInputChange} required disabled={isSubmitting} placeholder="Minimum 6 characters" minLength="6" />
          </div>

          <h3 style={{ marginTop: '24px', marginBottom: '16px', color: 'var(--text-color)' }}>Student Profile</h3>
          
          <div className="form-group">
            <label htmlFor="reg_no">Registration Number *</label>
            <input type="text" id="reg_no" name="reg_no" value={studentForm.reg_no} onChange={handleInputChange} required disabled={isSubmitting} placeholder="e.g., 2026CS001" />
          </div>
          <div className="form-group">
            <label htmlFor="dob">Date of Birth</label>
            <input type="date" id="dob" name="dob" value={studentForm.dob} onChange={handleInputChange} disabled={isSubmitting} />
          </div>
          <div className="form-group">
            <label htmlFor="gender">Gender</label>
            <select id="gender" name="gender" value={studentForm.gender} onChange={handleInputChange} disabled={isSubmitting}>
              <option value="">Select gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
              <option value="N">Prefer not to say</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input type="tel" id="phone" name="phone" value={studentForm.phone} onChange={handleInputChange} disabled={isSubmitting} placeholder="e.g., +91-9876543210" />
          </div>
          <div className="form-group">
            <label htmlFor="address">Address</label>
            <input type="text" id="address" name="address" value={studentForm.address} onChange={handleInputChange} disabled={isSubmitting} placeholder="Residential address" />
          </div>
          <div className="form-group">
            <label htmlFor="program_id">Program *</label>
            <select id="program_id" name="program_id" value={studentForm.program_id} onChange={handleInputChange} required disabled={isSubmitting}>
              <option value="">Select a program</option>
              {programs.map(program => (
                <option key={program.id} value={program.id}>{program.name} ({program.code})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="department_id">Department</label>
            <select id="department_id" name="department_id" value={studentForm.department_id} onChange={handleInputChange} disabled={isSubmitting}>
              <option value="">Select a department</option>
              {departments.map(dept => (
                <option key={dept.id} value={dept.id}>{dept.name} ({dept.code})</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="current_semester">Current Semester *</label>
            <input type="number" id="current_semester" name="current_semester" value={studentForm.current_semester} onChange={handleInputChange} required disabled={isSubmitting} min="1" max="20" />
          </div>
          <div className="form-group">
            <label htmlFor="batch_year">Batch Year *</label>
            <input type="number" id="batch_year" name="batch_year" value={studentForm.batch_year} onChange={handleInputChange} required disabled={isSubmitting} min="2000" max="2100" />
          </div>

          {customFields.length > 0 && (
            <>
              <h3 style={{ marginTop: '24px', marginBottom: '16px', color: 'var(--text-color)' }}>Custom Fields</h3>
              {customFields.map(field => (
                <div key={field.id} className="form-group">
                  <label htmlFor={`custom-${field.field_name}`}>
                    {field.field_label} {field.is_required && '*'}
                  </label>
                  {renderCustomField(field)}
                  {field.help_text && <small>{field.help_text}</small>}
                </div>
              ))}
            </>
          )}

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => { setIsAddModalOpen(false); resetForm(); }} disabled={isSubmitting}>Cancel</button>
            <button type="submit" className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`} disabled={isSubmitting || !isFormValid()}>
              {isSubmitting ? 'Adding...' : 'Add Student'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminStudents;
