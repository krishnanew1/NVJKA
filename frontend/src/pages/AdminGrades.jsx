import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminGrades.css';

const AdminGrades = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [expandedSubjects, setExpandedSubjects] = useState({});
  const [gradesData, setGradesData] = useState({});
  const [loadingGrades, setLoadingGrades] = useState({});
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

  // Toggle subject expansion to view grades
  const toggleSubjectExpansion = async (subjectId) => {
    const isExpanded = expandedSubjects[subjectId];
    
    setExpandedSubjects(prev => ({
      ...prev,
      [subjectId]: !isExpanded
    }));

    // Fetch grades if expanding and not already loaded
    if (!isExpanded && !gradesData[subjectId]) {
      await fetchGradesForSubject(subjectId);
    }
  };

  // Fetch grades for a specific subject
  const fetchGradesForSubject = async (subjectId) => {
    try {
      setLoadingGrades(prev => ({ ...prev, [subjectId]: true }));

      const response = await api.get('/api/exams/admin/subject-grades/', {
        params: { subject_id: subjectId }
      });

      setGradesData(prev => ({
        ...prev,
        [subjectId]: response.data
      }));

    } catch (err) {
      console.error('Error fetching grades:', err);
      if (err.response?.status === 404) {
        setGradesData(prev => ({
          ...prev,
          [subjectId]: { 
            grades: [], 
            statistics: { 
              total_students: 0, 
              average_percentage: 0, 
              pass_count: 0, 
              fail_count: 0, 
              pass_rate: 0 
            } 
          }
        }));
      } else {
        showToast('Failed to load grades. Please try again.', 'error');
      }
    } finally {
      setLoadingGrades(prev => ({ ...prev, [subjectId]: false }));
    }
  };

  // Get grade color class - updated for new grade scale
  const getGradeColorClass = (gradeLetter) => {
    if (['A', 'A-'].includes(gradeLetter)) return 'grade-excellent';
    if (['B', 'B-'].includes(gradeLetter)) return 'grade-good';
    if (['C', 'C-'].includes(gradeLetter)) return 'grade-average';
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
        <div className="error-icon"></div>
        <p className="error-text">{error}</p>
        <button onClick={fetchSubjects} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  const groupedSubjects = groupSubjectsByCourse();

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
        <h1>Grades Overview</h1>
        <p>View and monitor student grades across all subjects</p>
      </div>

      {/* Summary Statistics */}
      {subjects.length > 0 && (
        <div className="summary-section">
          <div className="summary-card">
            <div className="card-icon">📚</div>
            <div className="card-content">
              <h3 className="card-number">{subjects.length}</h3>
              <p className="card-label">Total Subjects</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📖</div>
            <div className="card-content">
              <h3 className="card-number">{Object.keys(groupedSubjects).length}</h3>
              <p className="card-label">Courses</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">✅</div>
            <div className="card-content">
              <h3 className="card-number">
                {subjects.filter(s => s.faculty_info).length}
              </h3>
              <p className="card-label">Subjects with Faculty</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <h3 className="card-number">
                {Object.keys(gradesData).length}
              </h3>
              <p className="card-label">Subjects Viewed</p>
            </div>
          </div>
        </div>
      )}

      {/* Subjects Grouped by Course */}
      {subjects.length > 0 ? (
        <div className="subjects-section">
          {Object.keys(groupedSubjects).sort().map(courseName => (
            <div key={courseName} className="course-group-card">
              <div className="course-header">
                <h2>{courseName}</h2>
                <span className="subject-count">
                  {groupedSubjects[courseName].length} subject{groupedSubjects[courseName].length !== 1 ? 's' : ''}
                </span>
              </div>

              <div className="subjects-table-container">
                <table className="subjects-table">
                  <thead>
                    <tr>
                      <th>Subject Code</th>
                      <th>Subject Name</th>
                      <th>Semester</th>
                      <th>Credits</th>
                      <th>Faculty</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {groupedSubjects[courseName].map(subject => (
                      <>
                        <tr key={subject.id} className="subject-row">
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
                              <span className="badge badge-warning">Not Assigned</span>
                            )}
                          </td>
                          <td>
                            <button
                              className={`btn-small ${expandedSubjects[subject.id] ? 'btn-secondary' : 'btn-primary'}`}
                              onClick={() => toggleSubjectExpansion(subject.id)}
                            >
                              {expandedSubjects[subject.id] ? '▲ Hide Grades' : '▼ View Grades'}
                            </button>
                          </td>
                        </tr>

                        {/* Expanded Grades Section */}
                        {expandedSubjects[subject.id] && (
                          <tr className="grades-expansion-row">
                            <td colSpan="6">
                              <div className="grades-expansion-content">
                                {loadingGrades[subject.id] ? (
                                  <div className="grades-loading">
                                    <div className="spinner"></div>
                                    <p>Loading grades...</p>
                                  </div>
                                ) : gradesData[subject.id] ? (
                                  <>
                                    {/* Statistics */}
                                    <div className="grades-statistics">
                                      <div className="stat-item">
                                        <span className="stat-label">Total Students:</span>
                                        <span className="stat-value">{gradesData[subject.id].statistics.total_students}</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Graded Students:</span>
                                        <span className="stat-value">{gradesData[subject.id].statistics.graded_students}</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Pending Grades:</span>
                                        <span className="stat-value warning">{gradesData[subject.id].statistics.ungraded_students}</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Class Average:</span>
                                        <span className="stat-value">{gradesData[subject.id].statistics.average_percentage}%</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Passed:</span>
                                        <span className="stat-value success">{gradesData[subject.id].statistics.pass_count}</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Failed:</span>
                                        <span className="stat-value error">{gradesData[subject.id].statistics.fail_count}</span>
                                      </div>
                                      <div className="stat-item">
                                        <span className="stat-label">Pass Rate:</span>
                                        <span className="stat-value">{gradesData[subject.id].statistics.pass_rate}%</span>
                                      </div>
                                    </div>

                                    {/* Grades Table */}
                                    {gradesData[subject.id].grades.length > 0 ? (
                                      <div className="grades-table-wrapper">
                                        <table className="grades-table">
                                          <thead>
                                            <tr>
                                              <th>Enrollment No.</th>
                                              <th>Student Name</th>
                                              <th>Marks Obtained</th>
                                              <th>Total Marks</th>
                                              <th>Percentage</th>
                                              <th>Grade</th>
                                              <th>Remarks</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {gradesData[subject.id].grades.map((grade, index) => (
                                              <tr key={grade.id || `student-${grade.student_id}`} className={!grade.has_grade ? 'ungraded-row' : ''}>
                                                <td className="enrollment-cell">{grade.student_enrollment}</td>
                                                <td className="name-cell">{grade.student_name}</td>
                                                <td className="marks-cell">
                                                  {grade.has_grade ? grade.marks_obtained : '-'}
                                                </td>
                                                <td className="marks-cell">
                                                  {grade.has_grade ? grade.total_marks : '-'}
                                                </td>
                                                <td className="percentage-cell">
                                                  {grade.has_grade ? (
                                                    <span className={`percentage-badge ${getGradeColorClass(grade.grade_letter)}`}>
                                                      {grade.percentage}%
                                                    </span>
                                                  ) : (
                                                    <span className="percentage-badge grade-pending">
                                                      Pending
                                                    </span>
                                                  )}
                                                </td>
                                                <td className="grade-cell">
                                                  {grade.has_grade ? (
                                                    <span className={`grade-badge ${getGradeColorClass(grade.grade_letter)}`}>
                                                      {grade.grade_letter}
                                                    </span>
                                                  ) : (
                                                    <span className="grade-badge grade-pending">
                                                      -
                                                    </span>
                                                  )}
                                                </td>
                                                <td className="remarks-cell">{grade.remarks || '-'}</td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                    ) : (
                                      <div className="no-grades-message">
                                        <p>📝 No students enrolled in this subject yet</p>
                                      </div>
                                    )}
                                  </>
                                ) : null}
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      ) : (
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
