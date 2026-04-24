import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './FacultyGrades.css';

const FacultyGrades = () => {
  // State management
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Grading modal state
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [isGradingModalOpen, setIsGradingModalOpen] = useState(false);
  const [students, setStudents] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [grades, setGrades] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Grade options
  const gradeOptions = [
    { value: 'A', label: 'A (90-100%)', points: 10 },
    { value: 'A-', label: 'A- (85-89%)', points: 9 },
    { value: 'B', label: 'B (80-84%)', points: 8 },
    { value: 'B-', label: 'B- (75-79%)', points: 7 },
    { value: 'C', label: 'C (70-74%)', points: 6 },
    { value: 'C-', label: 'C- (65-69%)', points: 5 },
    { value: 'D', label: 'D (60-64%)', points: 4 },
    { value: 'F', label: 'F (Below 60%)', points: 0 }
  ];

  // Fetch faculty's assigned subjects
  const fetchAssignments = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/academics/faculty/my-subjects/');
      
      let data;
      if (response.data.results) {
        data = response.data.results;
      } else if (Array.isArray(response.data)) {
        data = response.data;
      } else {
        data = [];
      }
      
      setAssignments(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      console.error('Error fetching assignments:', err);
      
      if (err.response?.status === 404) {
        setAssignments([]);
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Faculty privileges required.');
      } else {
        setError('Failed to load your assigned subjects. Please try again.');
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

  // Fetch students and their current grades for a subject
  const fetchStudentsAndGrades = async (subject) => {
    try {
      setLoadingStudents(true);
      
      // Get students enrolled in this subject
      const studentsResponse = await api.get('/api/students/subject-enrolled/', {
        params: {
          subject_id: subject.id
        }
      });

      const studentProfiles = studentsResponse.data.students.map(student => ({
        id: student.id,
        name: student.name,
        roll_number: student.roll_number,
        email: student.email,
        current_semester: student.current_semester,
        is_backlog: student.is_backlog
      }));

      setStudents(studentProfiles);

      // Get existing grades for this subject
      try {
        const gradesResponse = await api.get('/api/exams/admin/subject-grades/', {
          params: {
            subject_id: subject.id
          }
        });

        // Initialize grades with existing data or defaults
        const initialGrades = {};
        studentProfiles.forEach(student => {
          const existingGrade = gradesResponse.data.students.find(g => g.student_id === student.id);
          if (existingGrade && existingGrade.has_grade) {
            initialGrades[student.id] = {
              marks_obtained: existingGrade.marks_obtained || '',
              total_marks: existingGrade.total_marks || 100,
              grade_letter: existingGrade.grade_letter || '',
              remarks: existingGrade.remarks || ''
            };
          } else {
            initialGrades[student.id] = {
              marks_obtained: '',
              total_marks: 100,
              grade_letter: '',
              remarks: ''
            };
          }
        });

        setGrades(initialGrades);
      } catch (gradesErr) {
        // If grades endpoint fails, initialize with empty grades
        const initialGrades = {};
        studentProfiles.forEach(student => {
          initialGrades[student.id] = {
            marks_obtained: '',
            total_marks: 100,
            grade_letter: '',
            remarks: ''
          };
        });
        setGrades(initialGrades);
      }

    } catch (err) {
      console.error('Error fetching students:', err);
      if (err.response?.status === 404) {
        showToast('Subject not found or no students enrolled.', 'warning');
      } else if (err.response?.status === 403) {
        showToast('You can only view students for subjects assigned to you.', 'error');
      } else {
        showToast('Failed to load students. Please try again.', 'error');
      }
      setStudents([]);
    } finally {
      setLoadingStudents(false);
    }
  };

  // Handle grade input changes
  const handleGradeChange = (studentId, field, value) => {
    setGrades(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [field]: value
      }
    }));

    // Auto-calculate grade letter based on percentage
    if (field === 'marks_obtained' || field === 'total_marks') {
      const currentGrade = grades[studentId] || {};
      const marks = field === 'marks_obtained' ? parseFloat(value) : parseFloat(currentGrade.marks_obtained);
      const total = field === 'total_marks' ? parseFloat(value) : parseFloat(currentGrade.total_marks);

      if (!isNaN(marks) && !isNaN(total) && total > 0) {
        const percentage = (marks / total) * 100;
        let gradeLetter = 'F';

        if (percentage >= 90) gradeLetter = 'A';
        else if (percentage >= 85) gradeLetter = 'A-';
        else if (percentage >= 80) gradeLetter = 'B';
        else if (percentage >= 75) gradeLetter = 'B-';
        else if (percentage >= 70) gradeLetter = 'C';
        else if (percentage >= 65) gradeLetter = 'C-';
        else if (percentage >= 60) gradeLetter = 'D';

        setGrades(prev => ({
          ...prev,
          [studentId]: {
            ...prev[studentId],
            grade_letter: gradeLetter
          }
        }));
      }
    }
  };

  // Handle grade submission
  const handleSubmitGrades = async () => {
    if (!selectedSubject) return;

    setIsSubmitting(true);

    try {
      // Validate grades
      const gradesArray = [];
      const errors = [];

      Object.entries(grades).forEach(([studentId, grade]) => {
        if (grade.marks_obtained !== '' || grade.grade_letter !== '') {
          // Validate required fields
          if (!grade.marks_obtained || !grade.total_marks || !grade.grade_letter) {
            const student = students.find(s => s.id === parseInt(studentId));
            errors.push(`${student?.name || studentId}: All fields (marks, total, grade) are required`);
            return;
          }

          const marks = parseFloat(grade.marks_obtained);
          const total = parseFloat(grade.total_marks);

          if (isNaN(marks) || isNaN(total)) {
            const student = students.find(s => s.id === parseInt(studentId));
            errors.push(`${student?.name || studentId}: Marks must be valid numbers`);
            return;
          }

          if (marks < 0 || marks > total) {
            const student = students.find(s => s.id === parseInt(studentId));
            errors.push(`${student?.name || studentId}: Marks must be between 0 and ${total}`);
            return;
          }

          gradesArray.push({
            student_id: parseInt(studentId),
            marks_obtained: marks,
            total_marks: total,
            grade_letter: grade.grade_letter,
            remarks: grade.remarks || ''
          });
        }
      });

      if (errors.length > 0) {
        showToast(`Validation errors: ${errors.join(', ')}`, 'error');
        return;
      }

      if (gradesArray.length === 0) {
        showToast('Please enter grades for at least one student.', 'warning');
        return;
      }

      // Submit grades
      const payload = {
        subject_id: selectedSubject.id,
        grades: gradesArray
      };

      await api.post('/api/exams/faculty/grades/', payload);

      showToast(`Grades submitted successfully for ${gradesArray.length} students!`, 'success');
      setIsGradingModalOpen(false);
      setSelectedSubject(null);
      setStudents([]);
      setGrades({});
    } catch (err) {
      console.error('Error submitting grades:', err);
      if (err.response?.status === 400) {
        const errorMsg = err.response.data?.error || 'Invalid data. Please check your input.';
        showToast(errorMsg, 'error');
      } else if (err.response?.status === 403) {
        showToast('You are not authorized to submit grades for this subject.', 'error');
      } else {
        showToast('Failed to submit grades. Please try again.', 'error');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle subject click
  const handleSubjectClick = async (subject) => {
    setSelectedSubject(subject);
    setIsGradingModalOpen(true);
    await fetchStudentsAndGrades(subject);
  };

  // Close grading modal
  const closeGradingModal = () => {
    setIsGradingModalOpen(false);
    setSelectedSubject(null);
    setStudents([]);
    setGrades({});
  };

  // Calculate percentage
  const calculatePercentage = (marks, total) => {
    if (!marks || !total || isNaN(marks) || isNaN(total) || total === 0) return '';
    return ((parseFloat(marks) / parseFloat(total)) * 100).toFixed(1);
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <Loader message="Loading your assigned subjects..." size="large" />
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
    <div className="faculty-grades">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Dashboard Header */}
      <div className="grades-header">
        <h1>📊 Grade Management</h1>
        <p>Submit and manage grades for your assigned subjects</p>
      </div>

      {/* Summary Section */}
      <div className="summary-section">
        <div className="summary-card">
          <div className="card-icon">📚</div>
          <div className="card-content">
            <h3 className="card-number">{assignments ? assignments.length : 0}</h3>
            <p className="card-label">Assigned Subjects</p>
          </div>
        </div>
        <div className="summary-card">
          <div className="card-icon">🎓</div>
          <div className="card-content">
            <h3 className="card-number">
              {assignments && assignments.length > 0 
                ? new Set(assignments.map(a => a.semester).filter(Boolean)).size 
                : 0}
            </h3>
            <p className="card-label">Semesters</p>
          </div>
        </div>
      </div>

      {/* Subjects Grid */}
      <div className="subjects-section">
        <div className="section-header">
          <h2>My Assigned Subjects</h2>
          <p>Click on a subject to manage grades for enrolled students</p>
        </div>

        {assignments && assignments.length > 0 ? (
          <div className="subject-cards-grid">
            {assignments.map((subject) => (
              <div 
                key={subject.id} 
                className="subject-card"
                onClick={() => handleSubjectClick(subject)}
              >
                <div className="subject-card-header">
                  <div className="subject-icon">📖</div>
                  <div className="subject-badge">
                    {subject.semester_display || `Sem ${subject.semester}`}
                  </div>
                </div>
                <div className="subject-card-body">
                  <h3 className="subject-name">{subject.name || 'Unnamed Subject'}</h3>
                  <p className="subject-code">{subject.code || 'N/A'}</p>
                  <p className="subject-course">{subject.course?.name || 'N/A'}</p>
                  <p className="subject-credits">💳 {subject.credits || 0} Credits</p>
                </div>
                <div className="subject-card-footer">
                  <button 
                    className="grade-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSubjectClick(subject);
                    }}
                    title="Manage grades for this subject"
                  >
                    📊 Manage Grades
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📚</div>
            <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
              {assignments === null || assignments === undefined 
                ? 'Loading subjects...' 
                : 'No subjects assigned yet'}
            </p>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              {assignments === null || assignments === undefined
                ? 'Please wait while we fetch your data'
                : 'Your assigned subjects will appear here once the administration assigns them to you'}
            </p>
          </div>
        )}
      </div>

      {/* Grading Modal */}
      <Modal
        isOpen={isGradingModalOpen}
        onClose={closeGradingModal}
        title={`Manage Grades - ${selectedSubject?.name || ''}`}
      >
        <div className="grading-modal-content">
          {/* Subject Info */}
          {selectedSubject && (
            <div className="subject-info">
              <h3>{selectedSubject.name}</h3>
              <p>Code: {selectedSubject.code} | Credits: {selectedSubject.credits}</p>
            </div>
          )}

          {/* Students List */}
          {loadingStudents ? (
            <div className="modal-loading">
              <div className="spinner"></div>
              <p>Loading students...</p>
            </div>
          ) : students.length > 0 ? (
            <div className="grades-table-container">
              <table className="grades-table">
                <thead>
                  <tr>
                    <th>Roll No.</th>
                    <th>Student Name</th>
                    <th>Marks Obtained</th>
                    <th>Total Marks</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                    <th>Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.id}>
                      <td className="student-roll">{student.roll_number}</td>
                      <td className="student-name">
                        {student.name}
                        {student.is_backlog && <span className="backlog-badge">Backlog</span>}
                      </td>
                      <td className="marks-input">
                        <input
                          type="number"
                          min="0"
                          step="0.1"
                          value={grades[student.id]?.marks_obtained || ''}
                          onChange={(e) => handleGradeChange(student.id, 'marks_obtained', e.target.value)}
                          disabled={isSubmitting}
                          placeholder="0"
                        />
                      </td>
                      <td className="total-marks-input">
                        <input
                          type="number"
                          min="1"
                          step="0.1"
                          value={grades[student.id]?.total_marks || 100}
                          onChange={(e) => handleGradeChange(student.id, 'total_marks', e.target.value)}
                          disabled={isSubmitting}
                        />
                      </td>
                      <td className="percentage">
                        {calculatePercentage(
                          grades[student.id]?.marks_obtained,
                          grades[student.id]?.total_marks
                        )}%
                      </td>
                      <td className="grade-select">
                        <select
                          value={grades[student.id]?.grade_letter || ''}
                          onChange={(e) => handleGradeChange(student.id, 'grade_letter', e.target.value)}
                          disabled={isSubmitting}
                        >
                          <option value="">Select Grade</option>
                          {gradeOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="remarks-input">
                        <input
                          type="text"
                          value={grades[student.id]?.remarks || ''}
                          onChange={(e) => handleGradeChange(student.id, 'remarks', e.target.value)}
                          disabled={isSubmitting}
                          placeholder="Optional remarks"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-students">
              <p>No students found for this subject</p>
            </div>
          )}

          {/* Submit Button */}
          {students.length > 0 && (
            <div className="grading-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={closeGradingModal}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="button"
                className={`btn btn-primary ${isSubmitting ? 'btn-loading' : ''}`}
                onClick={handleSubmitGrades}
                disabled={isSubmitting || students.length === 0}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Grades'}
              </button>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default FacultyGrades;