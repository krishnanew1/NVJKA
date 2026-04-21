import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './StudentReports.css';

const StudentReports = () => {
  const [loading, setLoading] = useState(true);
  const [attendanceData, setAttendanceData] = useState([]);
  const [gradesData, setGradesData] = useState(null);
  const [studentInfo, setStudentInfo] = useState(null);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch all report data
  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch attendance data
      const attendanceResponse = await api.get('/api/attendance/my-records/');
      const attendanceInfo = attendanceResponse.data || {};
      setAttendanceData(attendanceInfo.attendance || []);

      // Fetch grades data
      try {
        const gradesResponse = await api.get('/api/exams/students/my-grades/');
        setGradesData(gradesResponse.data);
        setStudentInfo(gradesResponse.data.student);
      } catch (gradesErr) {
        if (gradesErr.response?.status === 404) {
          setGradesData({ grades: [], statistics: { total_subjects: 0, average_percentage: 0, cgpa: 0 } });
        }
      }

    } catch (err) {
      console.error('Error fetching report data:', err);
      
      if (err.response?.status === 403) {
        setError('Access denied. Student privileges required.');
      } else {
        setError('Failed to load reports. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportData();
  }, []);

  // Toast helpers
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Calculate overall attendance
  const calculateOverallAttendance = () => {
    if (attendanceData.length === 0) return 0;
    
    let totalClasses = 0;
    let totalPresent = 0;
    
    attendanceData.forEach(record => {
      totalClasses += record.total_classes;
      totalPresent += record.present + record.late;
    });
    
    return totalClasses > 0 ? Math.round((totalPresent / totalClasses) * 100) : 0;
  };

  // Get attendance color
  const getAttendanceColor = (percentage) => {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 75) return 'good';
    if (percentage >= 60) return 'average';
    return 'poor';
  };

  // Get grade color
  const getGradeColor = (gradeLetter) => {
    if (['A+', 'A'].includes(gradeLetter)) return 'excellent';
    if (['B+', 'B'].includes(gradeLetter)) return 'good';
    if (['C+', 'C'].includes(gradeLetter)) return 'average';
    if (gradeLetter === 'D') return 'pass';
    return 'fail';
  };

  if (loading) {
    return <Loader message="Loading your reports..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchReportData} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  const overallAttendance = calculateOverallAttendance();

  return (
    <div className="student-reports">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="reports-header">
        <h1>📈 My Academic Reports</h1>
        <p>Comprehensive view of your attendance and academic performance</p>
      </div>

      {/* Student Info Card */}
      {studentInfo && (
        <div className="student-info-card">
          <div className="info-icon">👨‍🎓</div>
          <div className="info-content">
            <h3>{studentInfo.name}</h3>
            <p>Enrollment: {studentInfo.enrollment_number}</p>
          </div>
        </div>
      )}

      {/* Overall Statistics */}
      <div className="overall-stats">
        <h2>📊 Overall Performance</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-content">
              <h3 className="stat-number">{attendanceData.length}</h3>
              <p className="stat-label">Enrolled Subjects</p>
            </div>
          </div>
          <div className={`stat-card ${getAttendanceColor(overallAttendance)}-card`}>
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <h3 className="stat-number">{overallAttendance}%</h3>
              <p className="stat-label">Overall Attendance</p>
            </div>
          </div>
          {gradesData?.statistics && (
            <>
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <h3 className="stat-number">{gradesData.statistics.average_percentage}%</h3>
                  <p className="stat-label">Average Marks</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⭐</div>
                <div className="stat-content">
                  <h3 className="stat-number">{gradesData.statistics.cgpa}</h3>
                  <p className="stat-label">CGPA</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Attendance Report */}
      <div className="report-section">
        <h2>📋 Attendance Report</h2>
        {attendanceData.length > 0 ? (
          <div className="report-table-container">
            <table className="report-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Code</th>
                  <th>Total Classes</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Late</th>
                  <th>Attendance %</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.map((record) => (
                  <tr key={record.subject.id}>
                    <td className="subject-name">{record.subject.name}</td>
                    <td className="subject-code">{record.subject.code}</td>
                    <td className="center-text">{record.total_classes}</td>
                    <td className="center-text success-text">{record.present}</td>
                    <td className="center-text danger-text">{record.absent}</td>
                    <td className="center-text warning-text">{record.late}</td>
                    <td className="center-text">
                      {record.percentage}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-section">
            <p>No attendance data available</p>
          </div>
        )}
      </div>

      {/* Grades Report */}
      <div className="report-section">
        <h2>🎓 Grades Report</h2>
        {gradesData?.grades && gradesData.grades.length > 0 ? (
          <div className="report-table-container">
            <table className="report-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Code</th>
                  <th>Marks</th>
                  <th>Percentage</th>
                  <th>Grade</th>
                  <th>Faculty</th>
                </tr>
              </thead>
              <tbody>
                {gradesData.grades.map((grade) => (
                  <tr key={grade.id}>
                    <td className="subject-name">{grade.subject_name}</td>
                    <td className="subject-code">{grade.subject_code}</td>
                    <td className="center-text">
                      {grade.marks_obtained} / {grade.total_marks}
                    </td>
                    <td className="center-text">
                      {grade.percentage}%
                    </td>
                    <td className="center-text">
                      {grade.grade_letter}
                    </td>
                    <td className="faculty-name">{grade.faculty_name || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-section">
            <p>No grades available yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentReports;
