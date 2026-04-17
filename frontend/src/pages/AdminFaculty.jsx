import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';
import './AdminFaculty.css';

const AdminFaculty = () => {
  // State management
  const [faculty, setFaculty] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [facultyForm, setFacultyForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });

  // Subject assignment state
  const [subjectAssignments, setSubjectAssignments] = useState({});
  const [savingAssignments, setSavingAssignments] = useState({});

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [facultyRes, subjectsRes, deptsRes] = await Promise.all([
        api.get('/api/users/faculty/'),
        api.get('/api/academics/subjects/'),
        api.get('/api/academics/departments/')
      ]);

      const facultyData = facultyRes.data.results || facultyRes.data || [];
      const subjectsData = subjectsRes.data.results || subjectsRes.data || [];
      const deptsData = deptsRes.data.results || deptsRes.data || [];

      setFaculty(Array.isArray(facultyData) ? facultyData : []);
      setSubjects(Array.isArray(subjectsData) ? subjectsData : []);
      setDepartments(Array.isArray(deptsData) ? deptsData : []);

      // Initialize subject assignments with current faculty
      const assignments = {};
      subjectsData.forEach(subject => {
        assignments[subject.id] = subject.faculty_info?.id || '';
      });
      setSubjectAssignments(assignments);

      setError('');
    } catch (err) {
      console.error('Error fetching data:', err);
      if (err.response) {
        setError(`Failed to load data: ${err.response.status} ${err.response.statusText}`);
      } else if (err.request) {
        setError('Network error. Please check your connection and try again.');
      } else {
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
    setFacultyForm(prev => ({ ...prev, [name]: value }));
  };

  const isFormValid = () => {
    return (
      facultyForm.first_name.trim().length > 0 &&
      facultyForm.last_name.trim().length > 0 &&
      facultyForm.email.trim().length > 0 &&
      facultyForm.password.length >= 6
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
      // Generate username from email
      const username = facultyForm.email.split('@')[0];

      const data = {
        user: {
          username: username,
          email: facultyForm.email,
          first_name: facultyForm.first_name,
          last_name: facultyForm.last_name,
          password: facultyForm.password,
          role: 'FACULTY'
        },
        profile: {
          employee_id: `FAC${Date.now().toString().slice(-6)}`, // Generate temp employee ID
          designation: 'Assistant Professor',
          department_id: departments[0]?.id || null
        }
      };

      await api.post('/api/users/register/', data);
      setIsAddModalOpen(false);
      resetForm();
      await fetchData();
      showToast('Faculty member added successfully!', 'success');
    } catch (err) {
      console.error('Error adding faculty:', err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Failed to add faculty member.';
      showToast(errorMsg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFacultyForm({
      first_name: '',
      last_name: '',
      email: '',
      password: ''
    });
  };

  // Subject assignment handlers
  const handleAssignmentChange = (subjectId, facultyId) => {
    setSubjectAssignments(prev => ({
      ...prev,
      [subjectId]: facultyId
    }));
  };

  const handleSaveAssignment = async (subjectId) => {
    const facultyId = subjectAssignments[subjectId];
    const subject = subjects.find(s => s.id === subjectId);

    setSavingAssignments(prev => ({ ...prev, [subjectId]: true }));

    try {
      const response = await api.patch(
        `/api/academics/subjects/${subjectId}/assign-faculty/`,
        { faculty_id: facultyId || null }
      );

      if (response.data.success) {
        // Update the subject in state with new faculty info
        setSubjects(prev => prev.map(s => 
          s.id === subjectId 
            ? { ...s, faculty_info: response.data.data.faculty_info }
            : s
        ));

        const facultyName = faculty.find(f => f.id === parseInt(facultyId))?.user?.full_name || 'None';
        showToast(
          facultyId 
            ? `${facultyName} assigned to ${subject.name}` 
            : `Faculty unassigned from ${subject.name}`,
          'success'
        );
      }
    } catch (err) {
      console.error('Error saving assignment:', err);
      const errorMsg = err.response?.data?.error || 'Failed to save assignment.';
      showToast(errorMsg, 'error');
    } finally {
      setSavingAssignments(prev => ({ ...prev, [subjectId]: false }));
    }
  };

  // Group subjects by course
  const groupSubjectsByCourse = () => {
    const grouped = {};
    subjects.forEach(subject => {
      const courseName = subject.course?.name || 'No Course';
      if (!grouped[courseName]) {
        grouped[courseName] = [];
      }
      grouped[courseName].push(subject);
    });
    return grouped;
  };

  if (loading) return <Loader message="Loading faculty data..." size="large" />;
  if (error) return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{error}</p>
      <button onClick={fetchData} className="retry-button">Retry</button>
    </div>
  );

  const groupedSubjects = groupSubjectsByCourse();

  return (
    <div className="admin-dashboard">
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} onClose={hideToast} />

      <div className="dashboard-header">
        <h1>👨‍🏫 Faculty Management</h1>
        <p>Manage faculty members and subject assignments</p>
      </div>

      <div className="summary-section">
        <div className="summary-card">
          <div className="card-icon">👨‍🏫</div>
          <div className="card-content">
            <h3 className="card-number">{faculty.length}</h3>
            <p className="card-label">Total Faculty</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon">📚</div>
          <div className="card-content">
            <h3 className="card-number">{subjects.length}</h3>
            <p className="card-label">Total Subjects</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon">✓</div>
          <div className="card-content">
            <h3 className="card-number">
              {subjects.filter(s => s.faculty_info).length}
            </h3>
            <p className="card-label">Assigned Subjects</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon">⏳</div>
          <div className="card-content">
            <h3 className="card-number">
              {subjects.filter(s => !s.faculty_info).length}
            </h3>
            <p className="card-label">Unassigned Subjects</p>
          </div>
        </div>
      </div>

      <div className="tables-section">
        {/* Faculty List */}
        <div className="table-card">
          <div className="table-header">
            <h2>Faculty Members</h2>
            <button className="add-btn" onClick={() => setIsAddModalOpen(true)}>
              + Add Faculty
            </button>
          </div>
          <div className="table-container">
            {faculty.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Designation</th>
                    <th>Department</th>
                    <th>Subjects</th>
                  </tr>
                </thead>
                <tbody>
                  {faculty.map(member => {
                    const assignedSubjects = subjects.filter(
                      s => s.faculty_info?.id === member.id
                    );
                    return (
                      <tr key={member.id}>
                        <td className="table-code">{member.employee_id}</td>
                        <td className="table-name">
                          {member.user?.full_name || member.user?.username}
                        </td>
                        <td>{member.user?.email}</td>
                        <td>{member.designation}</td>
                        <td>{member.department?.name || 'N/A'}</td>
                        <td>
                          <span className="badge badge-info">
                            {assignedSubjects.length} subject{assignedSubjects.length !== 1 ? 's' : ''}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">👨‍🏫</div>
                <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                  No faculty members found
                </p>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                  Click "Add Faculty" to register the first faculty member!
                </p>
                <button className="add-btn" onClick={() => setIsAddModalOpen(true)}>
                  + Add First Faculty
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Subject Assignment Section */}
        <div className="table-card" style={{ gridColumn: '1 / -1' }}>
          <div className="table-header">
            <h2>📚 Assign Subjects to Faculty</h2>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: 0 }}>
              Select a faculty member for each subject and click Save Assignment
            </p>
          </div>
          <div className="table-container">
            {subjects.length > 0 && faculty.length > 0 ? (
              <div className="assignment-section">
                {Object.keys(groupedSubjects).sort().map(courseName => (
                  <div key={courseName} className="course-assignment-group">
                    <h3 className="course-title">🎓 {courseName}</h3>
                    <table className="data-table assignment-table">
                      <thead>
                        <tr>
                          <th>Subject Code</th>
                          <th>Subject Name</th>
                          <th>Semester</th>
                          <th>Credits</th>
                          <th>Current Faculty</th>
                          <th>Assign Faculty</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {groupedSubjects[courseName].map(subject => {
                          const currentFacultyId = subjectAssignments[subject.id];
                          const hasChanged = currentFacultyId !== (subject.faculty_info?.id || '');
                          
                          return (
                            <tr key={subject.id}>
                              <td className="table-code">{subject.code}</td>
                              <td className="table-name">{subject.name}</td>
                              <td>{subject.semester_display}</td>
                              <td>{subject.credits}</td>
                              <td>
                                {subject.faculty_info ? (
                                  <span className="badge badge-success">
                                    {subject.faculty_info.name}
                                  </span>
                                ) : (
                                  <span className="badge badge-warning">Unassigned</span>
                                )}
                              </td>
                              <td>
                                <select
                                  value={currentFacultyId}
                                  onChange={(e) => handleAssignmentChange(subject.id, e.target.value)}
                                  className="assignment-select"
                                  disabled={savingAssignments[subject.id]}
                                >
                                  <option value="">-- Select Faculty --</option>
                                  {faculty.map(member => (
                                    <option key={member.id} value={member.id}>
                                      {member.user?.full_name || member.user?.username} ({member.employee_id})
                                    </option>
                                  ))}
                                </select>
                              </td>
                              <td>
                                <button
                                  className={`btn-small ${hasChanged ? 'btn-primary' : 'btn-secondary'}`}
                                  onClick={() => handleSaveAssignment(subject.id)}
                                  disabled={savingAssignments[subject.id] || !hasChanged}
                                >
                                  {savingAssignments[subject.id] ? (
                                    '⏳ Saving...'
                                  ) : hasChanged ? (
                                    '💾 Save'
                                  ) : (
                                    '✓ Saved'
                                  )}
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            ) : subjects.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📚</div>
                <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                  No subjects found
                </p>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Create subjects in the Academics section first
                </p>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">👨‍🏫</div>
                <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                  No faculty members available
                </p>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                  Add faculty members first to assign them to subjects
                </p>
                <button className="add-btn" onClick={() => setIsAddModalOpen(true)}>
                  + Add Faculty
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Faculty Modal */}
      <Modal 
        isOpen={isAddModalOpen} 
        onClose={() => { setIsAddModalOpen(false); resetForm(); }} 
        title="Add New Faculty Member"
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={facultyForm.first_name}
              onChange={handleInputChange}
              required
              disabled={isSubmitting}
              placeholder="e.g., John"
            />
          </div>

          <div className="form-group">
            <label htmlFor="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={facultyForm.last_name}
              onChange={handleInputChange}
              required
              disabled={isSubmitting}
              placeholder="e.g., Smith"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={facultyForm.email}
              onChange={handleInputChange}
              required
              disabled={isSubmitting}
              placeholder="e.g., john.smith@university.edu"
            />
            <small>Username will be generated from email</small>
          </div>

          <div className="form-group">
            <label htmlFor="password">Temporary Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={facultyForm.password}
              onChange={handleInputChange}
              required
              disabled={isSubmitting}
              placeholder="Minimum 6 characters"
              minLength="6"
            />
            <small>Faculty can change this after first login</small>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => { setIsAddModalOpen(false); resetForm(); }}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
              disabled={isSubmitting || !isFormValid()}
            >
              {isSubmitting ? 'Adding...' : 'Add Faculty'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminFaculty;
