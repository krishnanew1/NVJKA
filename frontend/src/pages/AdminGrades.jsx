import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminGrades.css';

const AdminGrades = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [gradesData, setGradesData] = useState(null);
  const [loadingGrades, setLoadingGrades] = useState(false);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch all subjects
  const fetchSubjects = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/academics/subjects/');
      const data = response.data.results || response.data;
      
      setSubjects(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching subjects:', err);
      if (err.response?.status === 404) {
        setSubjects([]);
      } else {
        setError('Failed to load subjects. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
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

  // Handle subject selection
  const handleSubjectChange = async (e) => {
    const subjectId = e.target.value;
    
    if (!subjectId) {
      setSelectedSubject(null);
      setGradesData(null);
      return;
    }

    const subject = subjects.find(s => s.id === parseInt(subjectId));
    setSelectedSubject(subject);

    // Fetch grades for this subject
    await fetchGradesForSubject(subjectId);
  };

  // Fetch grades for selected subject
  const fetchGradesForSubject = async (subjectId) => {
    try {
      setLoadingGrades(true);

      const response = await api.get('/api/exams/admin/subject-grades/', {
        params: { subject_id: subjectId }
      });

      setGradesData(response.data);

    } catch (err) {
      console.error('Error fetching grades:', err);
      if (err.response?.status === 404) {
        setGradesData({ grades: [], statistics: { total_students: 0, average_percentage: 0, pass_count: 0, fail_count: 0, pass_rate: 0 } });
      } else {
        showToast('Failed to load grades. Please try again.', 'error');
      }
    } finally {
      setLoadingGrades(false);
    }
  };

  // Get grade color class
  const getGradeColorClass = (gradeLetter) => {
    if (['A+', 'A'].includes(gradeLetter)) return 'grade-excellent';
    if (['B+', 'B'].includes(gradeLetter)) return 'grade-good';
    if (['C+', 'C'].includes(gradeLetter)) return 'grade-average';
    if (gradeLetter === 'D') return 'grade-pass';
    if (gradeLetter === 'F') return 'grade-fail';
    return '';
  };

  // Loading state
  if (loading) {
    return <Loader message="Loading subjects..." size="large" />;
  }

  // Error state
  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchSubjects} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="admin-grades">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="grades-header">
        <h1>📊 Grades Overview</h1>
        <p>View and monitor student grades across all subjects</p>
      </div>

      {/* Subject Selection */}
      <div className="subject-selection-card">
        <label htmlFor="subject-select">Select Subject:</label>
        <select
          id="subject-select"
          value={selectedSubject?.id || ''}
          onChange={handleSubjectChange}
          disabled={subjects.length === 0}
        >
          <option value="">-- Choose a subject --</option>
          {subjects.map(subject => (
            <option key={subject.id} value={subject.id}>
              {subject.code} - {subject.name} (Sem {subject.semester})
            </option>
          ))}
        </select>
      </div>

      {/* Subject Info & Statistics */}
      {selectedSubject && gradesData && (
        <>
          {/* Subject Info Card */}
          <div className="subject-info-card">
            <div className="info-section">
              <h3>{gradesData.subject.name}</h3>
              <p>
                <strong>Code:</strong> {gradesData.subject.code} | 
                <strong> Course:</strong> {gradesData.subject.course || 'N/A'} | 
                <strong> Faculty:</strong> {gradesData.subject.faculty || 'Not Assigned'}
              </p>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="statistics-section">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-content">
                <h3 className="stat-number">{gradesData.statistics.total_students}</h3>
                <p className="stat-label">Total Students</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h3 className="stat-number">{gradesData.statistics.average_percentage}%</h3>
                <p className="stat-label">Class Average</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <h3 className="stat-number">{gradesData.statistics.pass_count}</h3>
                <p className="stat-label">Passed</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">❌</div>
              <div className="stat-content">
                <h3 className="stat-number">{gradesData.statistics.fail_count}</h3>
                <p className="stat-label">Failed</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-content">
                <h3 className="stat-number">{gradesData.statistics.pass_rate}%</h3>
                <p className="stat-label">Pass Rate</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Grades Table */}
      {selectedSubject && (
        <div className="grades-table-card">
          <div className="card-header">
            <h2>Student Grades</h2>
            <p>Read-only view of submitted grades</p>
          </div>

          {loadingGrades ? (
            <div className="table-loading">
              <div className="spinner"></div>
              <p>Loading grades...</p>
            </div>
          ) : gradesData && gradesData.grades.length > 0 ? (
            <div className="table-container">
              <table className="grades-table">
                <thead>
                  <tr>
                    <th>Enrollment No.</th>
                    <th>Student Name</th>
                    <th>Marks Obtained</th>
                    <th>Total Marks</th>
                    <th>Percentage</th>
                    <th>Grade Letter</th>
                    <th>Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {gradesData.grades.map(grade => (
                    <tr key={grade.id}>
                      <td className="enrollment-cell">{grade.student_enrollment}</td>
                      <td className="name-cell">{grade.student_name}</td>
                      <td className="marks-cell">{grade.marks_obtained}</td>
                      <td className="marks-cell">{grade.total_marks}</td>
                      <td className="percentage-cell">
                        <span className={`percentage-badge ${getGradeColorClass(grade.grade_letter)}`}>
                          {grade.percentage}%
                        </span>
                      </td>
                      <td className="grade-cell">
                        <span className={`grade-badge ${getGradeColorClass(grade.grade_letter)}`}>
                          {grade.grade_letter}
                        </span>
                      </td>
                      <td className="remarks-cell">{grade.remarks || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <p>No grades submitted for this subject yet</p>
            </div>
          )}
        </div>
      )}

      {/* Empty State - No Subject Selected */}
      {!selectedSubject && subjects.length > 0 && (
        <div className="empty-state">
          <div className="empty-icon">📚</div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Select a subject to view grades
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Choose a subject from the dropdown above to view student grades and statistics
          </p>
        </div>
      )}

      {/* Empty State - No Subjects */}
      {subjects.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📚</div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            No subjects available
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            No subjects have been created in the system yet
          </p>
        </div>
      )}
    </div>
  );
};

export default AdminGrades;
