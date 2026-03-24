import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const FacultyDashboard = () => {
  // State management
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Attendance modal state
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [isAttendanceModalOpen, setIsAttendanceModalOpen] = useState(false);
  const [students, setStudents] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [attendanceDate, setAttendanceDate] = useState(new Date().toISOString().split('T')[0]);
  const [attendanceRecords, setAttendanceRecords] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit attendance modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedClassForEdit, setSelectedClassForEdit] = useState(null);
  const [editDate, setEditDate] = useState('');
  const [editStudents, setEditStudents] = useState([]);
  const [editAttendanceRecords, setEditAttendanceRecords] = useState({});
  const [loadingEditData, setLoadingEditData] = useState(false);
  const [isUpdatingAttendance, setIsUpdatingAttendance] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch faculty assignments
  const fetchAssignments = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/faculty/assignments/');
      const data = response.data.results || response.data;
      setAssignments(data);
      
      // If no assignments, don't show error - just empty state
      if (!data || data.length === 0) {
        setError(''); // Clear any previous errors
      }
    } catch (err) {
      console.error('Error fetching assignments:', err);
      
      // Handle 404 as empty state, not an error
      if (err.response?.status === 404) {
        setAssignments([]);
        setError(''); // Don't show error for 404 - will show empty state instead
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Faculty privileges required.');
      } else {
        setError('Failed to load class assignments. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
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

  // Fetch students for a specific assignment
  const fetchStudentsForAssignment = async (assignment) => {
    try {
      setLoadingStudents(true);
      
      // Get students enrolled in the course and semester
      const response = await api.get('/api/students/enrollments/', {
        params: {
          course: assignment.subject.course?.id,
          semester: assignment.semester,
          status: 'Active'
        }
      });

      const enrollments = response.data.results || response.data;
      
      // Extract student profiles from enrollments
      const studentProfiles = enrollments.map(enrollment => ({
        id: enrollment.student.id,
        name: enrollment.student.user?.full_name || enrollment.student.user?.username || 'Unknown',
        roll_number: enrollment.student.roll_number || 'N/A',
        enrollment_id: enrollment.id
      }));

      setStudents(studentProfiles);

      // Initialize attendance records with 'Present' as default
      const initialRecords = {};
      studentProfiles.forEach(student => {
        initialRecords[student.id] = 'Present';
      });
      setAttendanceRecords(initialRecords);

    } catch (err) {
      console.error('Error fetching students:', err);
      showToast('Failed to load students. Please try again.', 'error');
      setStudents([]);
    } finally {
      setLoadingStudents(false);
    }
  };

  // Handle class card click
  const handleClassClick = async (assignment) => {
    setSelectedAssignment(assignment);
    setIsAttendanceModalOpen(true);
    await fetchStudentsForAssignment(assignment);
  };

  // Handle attendance status change
  const handleStatusChange = (studentId, status) => {
    setAttendanceRecords(prev => ({
      ...prev,
      [studentId]: status
    }));
  };

  // Handle attendance submission
  const handleSubmitAttendance = async () => {
    if (!selectedAssignment) return;

    setIsSubmitting(true);

    try {
      // Format records for API
      const records = Object.entries(attendanceRecords).map(([studentId, status]) => ({
        student_id: parseInt(studentId),
        status: status
      }));

      const payload = {
        subject_id: selectedAssignment.subject.id,
        date: attendanceDate,
        records: records
      };

      await api.post('/api/attendance/bulk-mark/', payload);

      showToast(`Attendance marked successfully for ${records.length} students!`, 'success');
      setIsAttendanceModalOpen(false);
      setSelectedAssignment(null);
      setStudents([]);
      setAttendanceRecords({});
    } catch (err) {
      console.error('Error submitting attendance:', err);
      if (err.response?.status === 400) {
        showToast('Invalid data. Please check your input.', 'error');
      } else if (err.response?.status === 403) {
        showToast('You are not authorized to mark attendance for this class.', 'error');
      } else if (err.response?.status === 409) {
        showToast('Attendance already marked for this date. Please choose a different date.', 'error');
      } else {
        showToast('Failed to submit attendance. Please try again.', 'error');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Close attendance modal
  const closeAttendanceModal = () => {
    setIsAttendanceModalOpen(false);
    setSelectedAssignment(null);
    setStudents([]);
    setAttendanceRecords({});
  };

  // Edit Past Attendance Functions
  const handleEditClick = (assignment) => {
    setSelectedClassForEdit(assignment);
    setEditDate('');
    setEditStudents([]);
    setEditAttendanceRecords({});
    setIsEditModalOpen(true);
  };

  const fetchPastAttendance = async () => {
    if (!selectedClassForEdit || !editDate) return;

    try {
      setLoadingEditData(true);
      
      const response = await api.get('/api/attendance/records/', {
        params: {
          subject_id: selectedClassForEdit.subject.id,
          date: editDate
        }
      });

      const data = response.data;
      setEditStudents(data.students || []);

      // Initialize attendance records with existing statuses
      const initialRecords = {};
      data.students.forEach(student => {
        initialRecords[student.student_id] = student.status || 'Present';
      });
      setEditAttendanceRecords(initialRecords);

      if (!data.has_records) {
        showToast('No attendance was marked on this date', 'info');
      }
    } catch (err) {
      console.error('Error fetching past attendance:', err);
      if (err.response?.status === 404) {
        showToast('No data found for this date', 'warning');
        setEditStudents([]);
      } else {
        showToast('Failed to load attendance data', 'error');
      }
    } finally {
      setLoadingEditData(false);
    }
  };

  useEffect(() => {
    if (editDate && selectedClassForEdit) {
      fetchPastAttendance();
    }
  }, [editDate]);

  const handleEditStatusChange = (studentId, status) => {
    setEditAttendanceRecords(prev => ({
      ...prev,
      [studentId]: status
    }));
  };

  const handleUpdateAttendance = async () => {
    if (!selectedClassForEdit || !editDate) return;

    setIsUpdatingAttendance(true);

    try {
      const records = Object.entries(editAttendanceRecords).map(([studentId, status]) => ({
        student_id: parseInt(studentId),
        status: status
      }));

      const payload = {
        subject_id: selectedClassForEdit.subject.id,
        date: editDate,
        records: records
      };

      await api.patch('/api/attendance/records/', payload);

      showToast(`Attendance updated successfully for ${records.length} students!`, 'success');
      closeEditModal();
    } catch (err) {
      console.error('Error updating attendance:', err);
      if (err.response?.status === 400) {
        showToast('Invalid data. Please check your input.', 'error');
      } else if (err.response?.status === 403) {
        showToast('You are not authorized to update attendance for this class.', 'error');
      } else {
        showToast('Failed to update attendance. Please try again.', 'error');
      }
    } finally {
      setIsUpdatingAttendance(false);
    }
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedClassForEdit(null);
    setEditDate('');
    setEditStudents([]);
    setEditAttendanceRecords({});
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <Loader message="Loading your class assignments..." size="large" />
  );

  // Error message component
  const ErrorMessage = () => (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{error}</p>
      <button 
        onClick={() => window.location.reload()} 
        className="retry-button"
      >
        Retry
      </button>
    </div>
  );

  // Show loading state
  if (loading) return <LoadingSpinner />;
  
  // Show error state
  if (error) return <ErrorMessage />;

  return (
    <div className="faculty-dashboard">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1>Faculty Dashboard</h1>
        <p>Manage your class assignments and mark attendance</p>
      </div>

      {/* Summary Section */}
      <div className="summary-section">
        <div className="summary-card">
          <div className="card-icon">📚</div>
          <div className="card-content">
            <h3 className="card-number">{assignments.length}</h3>
            <p className="card-label">Assigned Classes</p>
          </div>
        </div>
      </div>

      {/* Class Assignments Grid */}
      <div className="assignments-section">
        <div className="section-header">
          <h2>My Class Assignments</h2>
          <p>Click on a class to mark attendance</p>
        </div>

        {assignments.length > 0 ? (
          <div className="class-cards-grid">
            {assignments.map((assignment) => (
              <div 
                key={assignment.id} 
                className="class-card"
                onClick={() => handleClassClick(assignment)}
              >
                <div className="class-card-header">
                  <div className="class-icon">📖</div>
                  <div className="class-badge">
                    Sem {assignment.semester}
                  </div>
                </div>
                <div className="class-card-body">
                  <h3 className="class-name">{assignment.subject.name}</h3>
                  <p className="class-code">{assignment.subject.code}</p>
                  <p className="class-year">Academic Year: {assignment.academic_year}</p>
                </div>
                <div className="class-card-footer">
                  <button 
                    className="mark-attendance-btn"
                    onClick={() => handleClassClick(assignment)}
                  >
                    📋 Mark Attendance
                  </button>
                  <button 
                    className="edit-attendance-btn"
                    onClick={() => handleEditClick(assignment)}
                  >
                    ✏️ Edit Past Attendance
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">👋</div>
            <p>Welcome! You currently have no active class assignments</p>
            <p className="empty-subtext">Class assignments will appear here once they are created by the administration</p>
          </div>
        )}
      </div>

      {/* Attendance Modal */}
      <Modal
        isOpen={isAttendanceModalOpen}
        onClose={closeAttendanceModal}
        title={`Mark Attendance - ${selectedAssignment?.subject.name || ''}`}
      >
        <div className="attendance-modal-content">
          {/* Date Selector */}
          <div className="attendance-date-section">
            <label htmlFor="attendance-date">Attendance Date:</label>
            <input
              type="date"
              id="attendance-date"
              value={attendanceDate}
              onChange={(e) => setAttendanceDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              disabled={isSubmitting}
            />
          </div>

          {/* Students List */}
          {loadingStudents ? (
            <div className="modal-loading">
              <div className="spinner"></div>
              <p>Loading students...</p>
            </div>
          ) : students.length > 0 ? (
            <div className="attendance-table-container">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Roll No.</th>
                    <th>Student Name</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.id}>
                      <td className="student-roll">{student.roll_number}</td>
                      <td className="student-name">{student.name}</td>
                      <td className="student-status">
                        <div className="status-buttons">
                          <button
                            className={`status-btn ${attendanceRecords[student.id] === 'Present' ? 'active present' : ''}`}
                            onClick={() => handleStatusChange(student.id, 'Present')}
                            disabled={isSubmitting}
                          >
                            ✓ Present
                          </button>
                          <button
                            className={`status-btn ${attendanceRecords[student.id] === 'Absent' ? 'active absent' : ''}`}
                            onClick={() => handleStatusChange(student.id, 'Absent')}
                            disabled={isSubmitting}
                          >
                            ✗ Absent
                          </button>
                          <button
                            className={`status-btn ${attendanceRecords[student.id] === 'Late' ? 'active late' : ''}`}
                            onClick={() => handleStatusChange(student.id, 'Late')}
                            disabled={isSubmitting}
                          >
                            ⏰ Late
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-students">
              <p>No students found for this class</p>
            </div>
          )}

          {/* Submit Button */}
          {students.length > 0 && (
            <div className="attendance-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={closeAttendanceModal}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="button"
                className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
                onClick={handleSubmitAttendance}
                disabled={isSubmitting || students.length === 0}
              >
                {isSubmitting ? 'Saving...' : 'Save Attendance'}
              </button>
            </div>
          )}
        </div>
      </Modal>

      {/* Edit Past Attendance Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={closeEditModal}
        title={`Edit Past Attendance - ${selectedClassForEdit?.subject.name || ''}`}
      >
        <div className="edit-attendance-modal-content">
          {/* Date Picker */}
          <div className="edit-date-section">
            <label htmlFor="edit-attendance-date">Select Date:</label>
            <input
              type="date"
              id="edit-attendance-date"
              value={editDate}
              onChange={(e) => setEditDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              disabled={isUpdatingAttendance}
            />
          </div>

          {/* Loading State */}
          {loadingEditData && (
            <div className="modal-loading">
              <div className="spinner"></div>
              <p>Loading attendance data...</p>
            </div>
          )}

          {/* Students List */}
          {!loadingEditData && editStudents.length > 0 && (
            <>
              <div className="edit-info-message">
                {editStudents.some(s => s.status) ? (
                  <p>✏️ Editing attendance for {editDate}. Update the statuses below.</p>
                ) : (
                  <p>ℹ️ No attendance was marked on this date. You can mark it now.</p>
                )}
              </div>

              <div className="attendance-table-container">
                <table className="attendance-table">
                  <thead>
                    <tr>
                      <th>Roll No.</th>
                      <th>Student Name</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {editStudents.map((student) => (
                      <tr key={student.student_id}>
                        <td className="student-roll">{student.roll_number}</td>
                        <td className="student-name">{student.name}</td>
                        <td className="student-status">
                          <div className="status-buttons">
                            <button
                              className={`status-btn ${editAttendanceRecords[student.student_id] === 'Present' ? 'active present' : ''}`}
                              onClick={() => handleEditStatusChange(student.student_id, 'Present')}
                              disabled={isUpdatingAttendance}
                            >
                              ✓ Present
                            </button>
                            <button
                              className={`status-btn ${editAttendanceRecords[student.student_id] === 'Absent' ? 'active absent' : ''}`}
                              onClick={() => handleEditStatusChange(student.student_id, 'Absent')}
                              disabled={isUpdatingAttendance}
                            >
                              ✗ Absent
                            </button>
                            <button
                              className={`status-btn ${editAttendanceRecords[student.student_id] === 'Late' ? 'active late' : ''}`}
                              onClick={() => handleEditStatusChange(student.student_id, 'Late')}
                              disabled={isUpdatingAttendance}
                            >
                              ⏰ Late
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Update Button */}
              <div className="attendance-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeEditModal}
                  disabled={isUpdatingAttendance}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className={`btn btn-primary ${isUpdatingAttendance ? 'btn-loading' : ''}`}
                  onClick={handleUpdateAttendance}
                  disabled={isUpdatingAttendance || editStudents.length === 0}
                >
                  {isUpdatingAttendance ? 'Updating...' : 'Update Attendance'}
                </button>
              </div>
            </>
          )}

          {/* Empty State */}
          {!loadingEditData && editDate && editStudents.length === 0 && (
            <div className="no-students">
              <p>No students found for this class</p>
            </div>
          )}

          {/* No Date Selected */}
          {!loadingEditData && !editDate && (
            <div className="no-date-selected">
              <p>📅 Please select a date to view attendance records</p>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default FacultyDashboard;