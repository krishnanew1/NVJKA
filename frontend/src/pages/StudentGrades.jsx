import { useState, useEffect } from 'react';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentGrades = () => {
  const [grades, setGrades] = useState([]);
  const [cgpa, setCgpa] = useState(null);
  const [sgpa, setSgpa] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch grades data
  const fetchGrades = async () => {
    try {
      setLoading(true);
      setError('');

      // For now, we'll create mock data since the backend endpoint might not be fully implemented
      // In production, this would be: const response = await api.get('/api/exams/results/');
      
      const mockGrades = [];
      
      setGrades(mockGrades);
      setCgpa(null);
      setSgpa(null);
    } catch (err) {
      console.error('Error fetching grades:', err);
      
      if (err.response?.status === 404) {
        setGrades([]);
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else {
        setError('');
        setGrades([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGrades();
  }, []);

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Get grade color class
  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A':
      case 'A+':
        return 'grade-a';
      case 'B':
      case 'B+':
        return 'grade-b';
      case 'C':
      case 'C+':
        return 'grade-c';
      case 'D':
        return 'grade-d';
      case 'F':
        return 'grade-f';
      default:
        return '';
    }
  };

  const LoadingSpinner = () => (
    <Loader message="Loading your grades..." size="large" />
  );

  const ErrorMessage = () => (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <p className="error-text">{error}</p>
      <button onClick={() => window.location.reload()} className="retry-button">
        Retry
      </button>
    </div>
  );

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage />;

  return (
    <div className="student-grades">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      <div className="page-header">
        <h1>📊 My Grades & Transcript</h1>
        <p>View your academic performance</p>
      </div>

      {grades.length > 0 ? (
        <>
          {/* Transcript Summary */}
          <div className="transcript-summary">
            <div className="gpa-card">
              <div className="gpa-icon">🎓</div>
              <div className="gpa-content">
                <h3>CGPA</h3>
                <div className="gpa-value">{cgpa ? cgpa.toFixed(2) : 'N/A'}</div>
                <p>Cumulative Grade Point Average</p>
              </div>
            </div>
            <div className="gpa-card">
              <div className="gpa-icon">📈</div>
              <div className="gpa-content">
                <h3>SGPA</h3>
                <div className="gpa-value">{sgpa ? sgpa.toFixed(2) : 'N/A'}</div>
                <p>Semester Grade Point Average</p>
              </div>
            </div>
          </div>

          {/* Grades Table */}
          <div className="grades-section">
            <div className="section-header">
              <h2>Subject-wise Performance</h2>
            </div>

            <div className="grades-table-container">
              <table className="grades-table">
                <thead>
                  <tr>
                    <th>Subject Code</th>
                    <th>Subject Name</th>
                    <th>Marks Obtained</th>
                    <th>Total Marks</th>
                    <th>Percentage</th>
                    <th>Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {grades.map((grade, index) => (
                    <tr key={index}>
                      <td className="subject-code">{grade.subjectCode}</td>
                      <td className="subject-name">{grade.subjectName}</td>
                      <td className="marks-obtained">{grade.marksObtained}</td>
                      <td className="total-marks">{grade.totalMarks}</td>
                      <td className="percentage">{grade.percentage}%</td>
                      <td>
                        <span className={`grade-badge ${getGradeColor(grade.grade)}`}>
                          {grade.grade}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <p>No grades available for this semester</p>
          <p className="empty-subtext">Your exam results will appear here once they are published</p>
        </div>
      )}
    </div>
  );
};

export default StudentGrades;
