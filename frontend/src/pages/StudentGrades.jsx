import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './StudentGrades.css';

const StudentGrades = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [gradesData, setGradesData] = useState(null);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch student's grades
  const fetchGrades = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/exams/students/my-grades/');
      
      setGradesData(response.data);
    } catch (err) {
      console.error('Error fetching grades:', err);
      
      if (err.response?.status === 404) {
        setGradesData({ grades: [], statistics: { total_subjects: 0, average_percentage: 0, cgpa: 0 } });
      } else if (err.response?.status === 403) {
        setError('Access denied. Student privileges required.');
      } else {
        setError('Failed to load grades. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGrades();
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
    return <Loader message="Loading your grades..." size="large" />;
  }

  // Error state
  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchGrades} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="student-grades">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="grades-header">
        <h1>🎓 My Grades</h1>
        <p>View your academic performance and report card</p>
      </div>

      {/* Student Info Card */}
      {gradesData?.student && (
        <div className="student-info-card">
          <div className="info-icon">👨‍🎓</div>
          <div className="info-content">
            <h3>{gradesData.student.name}</h3>
            <p>Enrollment: {gradesData.student.enrollment_number}</p>
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      {gradesData?.statistics && (
        <div className="statistics-section">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-content">
              <h3 className="stat-number">{gradesData.statistics.total_subjects}</h3>
              <p className="stat-label">Total Subjects</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3 className="stat-number">{gradesData.statistics.average_percentage}%</h3>
              <p className="stat-label">Average Percentage</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <h3 className="stat-number">{gradesData.statistics.cgpa}</h3>
              <p className="stat-label">CGPA (out of 10)</p>
            </div>
          </div>
        </div>
      )}

      {/* Grades Table */}
      {gradesData?.grades && gradesData.grades.length > 0 ? (
        <div className="report-card">
          <div className="card-header">
            <h2>📋 Report Card</h2>
            <p>Your subject-wise grades and performance</p>
          </div>

          <div className="table-container">
            <table className="report-table">
              <thead>
                <tr>
                  <th>Subject Code</th>
                  <th>Subject Name</th>
                  <th>Marks</th>
                  <th>Percentage</th>
                  <th>Grade</th>
                  <th>Faculty</th>
                </tr>
              </thead>
              <tbody>
                {gradesData.grades.map((grade) => (
                  <tr key={grade.id}>
                    <td className="subject-code-cell">{grade.subject_code}</td>
                    <td className="subject-name-cell">{grade.subject_name}</td>
                    <td className="marks-cell">
                      {grade.marks_obtained} / {grade.total_marks}
                    </td>
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
                    <td className="faculty-cell">{grade.faculty_name || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Remarks Section */}
          {gradesData.grades.some(g => g.remarks) && (
            <div className="remarks-section">
              <h3>📝 Faculty Remarks</h3>
              {gradesData.grades
                .filter(g => g.remarks)
                .map(grade => (
                  <div key={grade.id} className="remark-item">
                    <strong>{grade.subject_name}:</strong> {grade.remarks}
                  </div>
                ))}
            </div>
          )}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            No grades available yet
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Your grades will appear here once your faculty submits them
          </p>
        </div>
      )}
    </div>
  );
};

export default StudentGrades;
