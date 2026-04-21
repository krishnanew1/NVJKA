import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminAcademics.css';

const AdminAcademics = () => {
  // State management
  const [departments, setDepartments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal states
  const [isDepartmentModalOpen, setIsDepartmentModalOpen] = useState(false);
  const [isCourseModalOpen, setIsCourseModalOpen] = useState(false);

  // Form states
  const [departmentForm, setDepartmentForm] = useState({
    name: '',
    code: '',
    description: ''
  });
  const [courseForm, setCourseForm] = useState({
    name: '',
    code: '',
    department: '',
    credits: '',
    duration_semesters: ''
  });

  // Loading states for forms
  const [isDepartmentSubmitting, setIsDepartmentSubmitting] = useState(false);
  const [isCourseSubmitting, setIsCourseSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Delete confirmation state
  const [deleteConfirmation, setDeleteConfirmation] = useState({
    isOpen: false,
    type: '', // 'department' or 'course'
    item: null,
    isDeleting: false
  });

  // Data fetching
  const fetchAcademicData = async () => {
    try {
      setLoading(true);
      setError('');

      // Make parallel GET requests to fetch departments and courses
      const [departmentsResponse, coursesResponse] = await Promise.all([
        api.get('/api/academics/departments/'),
        api.get('/api/academics/courses/')
      ]);

      // Handle paginated responses or direct arrays
      setDepartments(departmentsResponse.data.results || departmentsResponse.data);
      setCourses(coursesResponse.data.results || coursesResponse.data);
    } catch (err) {
      console.error('Error fetching academic data:', err);
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Admin privileges required.');
      } else if (err.response?.status === 500) {
        setError('Server error. Please try again later.');
      } else {
        setError('Failed to load academic data. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAcademicData();
  }, []);

  // Toast helper functions
  const showToast = (message, type = 'info') => {
    setToast({
      isVisible: true,
      message,
      type
    });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Department form handlers
  const handleDepartmentChange = (e) => {
    const { name, value } = e.target;
    setDepartmentForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Validate department form
  const isDepartmentFormValid = () => {
    return (
      departmentForm.name.trim().length > 0 &&
      departmentForm.code.trim().length > 0 &&
      /^[A-Z0-9_-]+$/i.test(departmentForm.code.trim())
    );
  };

  const handleDepartmentSubmit = async (e) => {
    e.preventDefault();
    
    if (!isDepartmentFormValid()) {
      showToast('Please fill all required fields correctly. Code should only contain letters, numbers, hyphens, or underscores.', 'error');
      return;
    }

    setIsDepartmentSubmitting(true);

    try {
      await api.post('/api/academics/departments/', departmentForm);
      
      setIsDepartmentModalOpen(false);
      setDepartmentForm({ name: '', code: '', description: '' });
      await fetchAcademicData();
      showToast('Department added successfully!', 'success');
    } catch (err) {
      console.error('Error adding department:', err);
      if (err.response?.status === 400) {
        const errorMsg = err.response.data?.detail || err.response.data?.message || 'Invalid data. Please check your input.';
        showToast(errorMsg, 'error');
      } else if (err.response?.status === 409) {
        showToast('Department code already exists.', 'error');
      } else {
        showToast('Failed to add department. Please try again.', 'error');
      }
    } finally {
      setIsDepartmentSubmitting(false);
    }
  };

  // Course form handlers
  const handleCourseChange = (e) => {
    const { name, value } = e.target;
    setCourseForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Validate course form
  const isCourseFormValid = () => {
    return (
      courseForm.name.trim().length > 0 &&
      courseForm.code.trim().length > 0 &&
      /^[A-Z0-9_-]+$/i.test(courseForm.code.trim()) &&
      courseForm.department !== ''
    );
  };

  const handleCourseSubmit = async (e) => {
    e.preventDefault();
    
    if (!isCourseFormValid()) {
      showToast('Please fill all required fields correctly. Code should only contain letters, numbers, hyphens, or underscores.', 'error');
      return;
    }

    setIsCourseSubmitting(true);

    try {
      const courseData = {
        name: courseForm.name,
        code: courseForm.code,
        department_id: parseInt(courseForm.department),
        credits: courseForm.credits ? parseInt(courseForm.credits) : null,
        duration_semesters: courseForm.duration_semesters ? parseInt(courseForm.duration_semesters) : null
      };

      await api.post('/api/academics/courses/', courseData);
      
      setIsCourseModalOpen(false);
      setCourseForm({ name: '', code: '', department: '', credits: '', duration_semesters: '' });
      await fetchAcademicData();
      showToast('Course added successfully!', 'success');
    } catch (err) {
      console.error('Error adding course:', err);
      if (err.response?.status === 400) {
        const errorMsg = err.response.data?.detail || err.response.data?.message || 'Invalid data. Please check your input.';
        showToast(errorMsg, 'error');
      } else if (err.response?.status === 409) {
        showToast('Course code already exists.', 'error');
      } else {
        showToast('Failed to add course. Please try again.', 'error');
      }
    } finally {
      setIsCourseSubmitting(false);
    }
  };

  // Modal close handlers
  const closeDepartmentModal = () => {
    setIsDepartmentModalOpen(false);
    setDepartmentForm({ name: '', code: '', description: '' });
  };

  const closeCourseModal = () => {
    setIsCourseModalOpen(false);
    setCourseForm({ name: '', code: '', department: '', credits: '', duration_semesters: '' });
  };

  // Delete handlers
  const handleDeleteClick = (type, item) => {
    setDeleteConfirmation({
      isOpen: true,
      type,
      item,
      isDeleting: false
    });
  };

  const handleDeleteConfirm = async () => {
    const { type, item } = deleteConfirmation;
    setDeleteConfirmation(prev => ({ ...prev, isDeleting: true }));

    try {
      const endpoint = type === 'department' 
        ? `/api/academics/departments/${item.id}/`
        : `/api/academics/courses/${item.id}/`;
      
      await api.delete(endpoint);
      
      setDeleteConfirmation({ isOpen: false, type: '', item: null, isDeleting: false });
      await fetchAcademicData();
      showToast(`${type === 'department' ? 'Department' : 'Course'} deleted successfully!`, 'success');
    } catch (err) {
      console.error(`Error deleting ${type}:`, err);
      if (err.response?.status === 400) {
        showToast(`Cannot delete ${type}. It may be in use by other records.`, 'error');
      } else if (err.response?.status === 404) {
        showToast(`${type === 'department' ? 'Department' : 'Course'} not found.`, 'error');
      } else {
        showToast(`Failed to delete ${type}. Please try again.`, 'error');
      }
    } finally {
      setDeleteConfirmation(prev => ({ ...prev, isDeleting: false }));
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmation({ isOpen: false, type: '', item: null, isDeleting: false });
  };

  if (loading) {
    return <Loader message="Loading academic data..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchAcademicData} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="admin-academics">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="academics-header">
        <h1>📚 Academic Management</h1>
        <p>Manage departments and courses</p>
      </div>

      {/* Data Tables Section */}
      <div className="tables-section">
        {/* Departments Table */}
        <div className="table-card">
          <div className="table-header">
            <h2>Departments</h2>
            <button 
              className="add-btn"
              onClick={() => setIsDepartmentModalOpen(true)}
            >
              + Add Department
            </button>
          </div>
          <div className="table-container">
            {departments.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Code</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((dept) => (
                    <tr key={dept.id}>
                      <td className="table-id">{dept.id}</td>
                      <td className="table-name">{dept.name}</td>
                      <td className="table-code">{dept.code}</td>
                      <td className="table-actions">
                        <button 
                          className="action-btn edit-btn"
                          onClick={() => showToast('Edit functionality coming soon!', 'info')}
                          title="Edit Department"
                        >
                          Edit
                        </button>
                        <button 
                          className="action-btn delete-btn"
                          onClick={() => handleDeleteClick('department', dept)}
                          title="Delete Department"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📂</div>
                <p>No departments found</p>
                <button 
                  className="add-btn"
                  onClick={() => setIsDepartmentModalOpen(true)}
                >
                  Add First Department
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Courses Table */}
        <div className="table-card">
          <div className="table-header">
            <h2>Courses</h2>
            <button 
              className="add-btn"
              onClick={() => setIsCourseModalOpen(true)}
            >
              + Add Course
            </button>
          </div>
          <div className="table-container">
            {courses.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Code</th>
                    <th>Department</th>
                    <th>Semesters</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((course) => (
                    <tr key={course.id}>
                      <td className="table-id">{course.id}</td>
                      <td className="table-name">{course.name}</td>
                      <td className="table-code">{course.code}</td>
                      <td className="table-department">
                        {course.department?.name || 'N/A'}
                      </td>
                      <td className="table-semesters">
                        {course.duration_semesters || course.duration_years ? 
                          (course.duration_semesters || (course.duration_years * 2)) : 'N/A'}
                      </td>
                      <td className="table-actions">
                        <button 
                          className="action-btn edit-btn"
                          onClick={() => showToast('Edit functionality coming soon!', 'info')}
                          title="Edit Course"
                        >
                          Edit
                        </button>
                        <button 
                          className="action-btn delete-btn"
                          onClick={() => handleDeleteClick('course', course)}
                          title="Delete Course"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📖</div>
                <p>No courses found</p>
                <button 
                  className="add-btn"
                  onClick={() => setIsCourseModalOpen(true)}
                >
                  Add First Course
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Department Modal */}
      <Modal
        isOpen={isDepartmentModalOpen}
        onClose={closeDepartmentModal}
        title="Add New Department"
      >
        <form onSubmit={handleDepartmentSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="dept-name">Department Name *</label>
            <input
              type="text"
              id="dept-name"
              name="name"
              value={departmentForm.name}
              onChange={handleDepartmentChange}
              required
              disabled={isDepartmentSubmitting}
              placeholder="e.g., Computer Science"
            />
          </div>

          <div className="form-group">
            <label htmlFor="dept-code">Department Code *</label>
            <input
              type="text"
              id="dept-code"
              name="code"
              value={departmentForm.code}
              onChange={handleDepartmentChange}
              required
              disabled={isDepartmentSubmitting}
              placeholder="e.g., CS"
              maxLength="10"
            />
          </div>

          <div className="form-group">
            <label htmlFor="dept-description">Description</label>
            <input
              type="text"
              id="dept-description"
              name="description"
              value={departmentForm.description}
              onChange={handleDepartmentChange}
              disabled={isDepartmentSubmitting}
              placeholder="Optional description"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={closeDepartmentModal}
              disabled={isDepartmentSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`btn btn-primary ${isDepartmentSubmitting ? 'btn-loading' : ''}`}
              disabled={isDepartmentSubmitting || !isDepartmentFormValid()}
            >
              {isDepartmentSubmitting ? 'Adding...' : 'Add Department'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Course Modal */}
      <Modal
        isOpen={isCourseModalOpen}
        onClose={closeCourseModal}
        title="Add New Course"
      >
        <form onSubmit={handleCourseSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="course-name">Course Name *</label>
            <input
              type="text"
              id="course-name"
              name="name"
              value={courseForm.name}
              onChange={handleCourseChange}
              required
              disabled={isCourseSubmitting}
              placeholder="e.g., Bachelor of Technology"
            />
          </div>

          <div className="form-group">
            <label htmlFor="course-code">Course Code *</label>
            <input
              type="text"
              id="course-code"
              name="code"
              value={courseForm.code}
              onChange={handleCourseChange}
              required
              disabled={isCourseSubmitting}
              placeholder="e.g., BTECH"
              maxLength="10"
            />
          </div>

          <div className="form-group">
            <label htmlFor="course-department">Department *</label>
            <select
              id="course-department"
              name="department"
              value={courseForm.department}
              onChange={handleCourseChange}
              required
              disabled={isCourseSubmitting}
            >
              <option value="">Select a department</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name} ({dept.code})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="course-credits">Total Credits</label>
            <input
              type="number"
              id="course-credits"
              name="credits"
              value={courseForm.credits}
              onChange={handleCourseChange}
              disabled={isCourseSubmitting}
              placeholder="e.g., 160"
              min="1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="course-duration">Duration (Semesters)</label>
            <input
              type="number"
              id="course-duration"
              name="duration_semesters"
              value={courseForm.duration_semesters}
              onChange={handleCourseChange}
              disabled={isCourseSubmitting}
              placeholder="e.g., 8"
              min="1"
              max="20"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={closeCourseModal}
              disabled={isCourseSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`btn btn-primary ${isCourseSubmitting ? 'btn-loading' : ''}`}
              disabled={isCourseSubmitting || !isCourseFormValid()}
            >
              {isCourseSubmitting ? 'Adding...' : 'Add Course'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteConfirmation.isOpen}
        onClose={handleDeleteCancel}
        title={`Delete ${deleteConfirmation.type === 'department' ? 'Department' : 'Course'}`}
      >
        <div className="delete-confirmation">
          <div className="delete-warning">
            <div className="warning-icon">⚠️</div>
            <div className="warning-content">
              <h3>Are you sure?</h3>
              <p>
                You are about to delete the {deleteConfirmation.type} "
                <strong>{deleteConfirmation.item?.name}</strong>" ({deleteConfirmation.item?.code}).
              </p>
              <p className="warning-text">
                This action cannot be undone. {deleteConfirmation.type === 'department' 
                  ? 'All courses in this department may be affected.' 
                  : 'All related data will be permanently removed.'}
              </p>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDeleteCancel}
              disabled={deleteConfirmation.isDeleting}
            >
              Cancel
            </button>
            <button
              type="button"
              className={`btn btn-danger ${deleteConfirmation.isDeleting ? 'btn-loading' : ''}`}
              onClick={handleDeleteConfirm}
              disabled={deleteConfirmation.isDeleting}
            >
              {deleteConfirmation.isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AdminAcademics;
