import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './FacultyAttendance.css';

const FacultyAttendance = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [attendanceData, setAttendanceData] = useState(null);
  
  // Accordion state - track which items are expanded
  const [expandedSubjects, setExpandedSubjects] = useState({});
  const [expandedBatches, setExpandedBatches] = useState({});
  const [expandedBranches, setExpandedBranches] = useState({});
  
  // Submission state - track which reports have been submitted
  const [submittedReports, setSubmittedReports] = useState({});
  const [submittingReports, setSubmittingReports] = useState({});

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch attendance summary data
  const fetchAttendanceSummary = async () => {
    try {
      setLoading(true);
      setError('');

      console.log('🔍 Fetching attendance summary from: /api/attendance/faculty/summary/');
      
      const response = await api.get('/api/attendance/faculty/summary/');
      
      console.log('📡 API Response:', response.data);
      
      setAttendanceData(response.data);
      
      // Initialize expanded state for first subject
      if (response.data.subjects && response.data.subjects.length > 0) {
        const firstSubjectId = response.data.subjects[0].subject.id;
        setExpandedSubjects({ [firstSubjectId]: true });
      }
      
    } catch (err) {
      console.error('❌ Error fetching attendance summary:', err);
      
      if (err.response?.status === 404) {
        setAttendanceData({ subjects: [] });
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response?.status === 403) {
        setError('Access denied. Faculty privileges required.');
      } else {
        setError('Failed to load attendance data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttendanceSummary();
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

  // Toggle accordion functions
  const toggleSubject = (subjectId) => {
    setExpandedSubjects(prev => ({
      ...prev,
      [subjectId]: !prev[subjectId]
    }));
  };

  const toggleBatch = (subjectId, batchString) => {
    const key = `${subjectId}-${batchString}`;
    setExpandedBatches(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const toggleBranch = (subjectId, batchString, branchCode) => {
    const key = `${subjectId}-${batchString}-${branchCode}`;
    setExpandedBranches(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Extract branch/program from reg_no
  const extractBranch = (regNo) => {
    // Assuming format: YYYY[Branch]NNN (e.g., 2024IMG001)
    // Extract characters after year (positions 4-6 or 4-7)
    if (regNo.length >= 7) {
      return regNo.substring(4, 7).toUpperCase();
    }
    return 'UNK';
  };

  // Group students by branch within a batch
  const groupStudentsByBranch = (students) => {
    const branches = {};
    
    students.forEach(student => {
      const branch = extractBranch(student.reg_no);
      
      if (!branches[branch]) {
        branches[branch] = [];
      }
      
      branches[branch].push(student);
    });
    
    return branches;
  };

  // Get attendance color class
  const getAttendanceColorClass = (percentage) => {
    if (percentage >= 75) return 'attendance-good';
    return 'attendance-poor';
  };

  // Handle submit report
  const handleSubmitReport = async (subjectId, batchString, branchCode) => {
    const reportKey = `${subjectId}-${batchString}-${branchCode}`;
    
    // Prevent double submission
    if (submittedReports[reportKey] || submittingReports[reportKey]) {
      return;
    }

    try {
      setSubmittingReports(prev => ({ ...prev, [reportKey]: true }));

      const payload = {
        subject_id: subjectId,
        batch_string: `${batchString}-${branchCode}`
      };

      console.log('📤 Submitting report:', payload);

      await api.post('/api/attendance/faculty/submit-report/', payload);

      showToast('Attendance report sent to Admin successfully!', 'success');
      
      // Mark as submitted
      setSubmittedReports(prev => ({ ...prev, [reportKey]: true }));

    } catch (err) {
      console.error('❌ Error submitting report:', err);
      
      if (err.response?.status === 400) {
        showToast('Invalid data. Please try again.', 'error');
      } else if (err.response?.status === 403) {
        showToast('You are not authorized to submit this report.', 'error');
      } else if (err.response?.status === 404) {
        showToast('Subject not found.', 'error');
      } else {
        showToast('Failed to submit report. Please try again.', 'error');
      }
    } finally {
      setSubmittingReports(prev => ({ ...prev, [reportKey]: false }));
    }
  };

  // Loading state
  if (loading) {
    return <Loader message="Loading attendance data..." size="large" />;
  }

  // Error state
  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon"></div>
        <p className="error-text">{error}</p>
        <button onClick={fetchAttendanceSummary} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="faculty-attendance">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="attendance-header">
        <h1>Master Attendance Report</h1>
        <p>View and submit attendance reports by batch and branch</p>
      </div>

      {/* Faculty Info */}
      {attendanceData?.faculty && (
        <div className="faculty-info-card">
          <div className="info-icon"></div>
          <div className="info-content">
            <h3>{attendanceData.faculty.name}</h3>
            <p>Employee ID: {attendanceData.faculty.employee_id}</p>
          </div>
        </div>
      )}

      {/* Attendance Data */}
      {attendanceData?.subjects && attendanceData.subjects.length > 0 ? (
        <div className="attendance-content">
          {attendanceData.subjects.map((subjectData) => {
            const subject = subjectData.subject;
            const batches = subjectData.batches;
            const isSubjectExpanded = expandedSubjects[subject.id];

            return (
              <div key={subject.id} className="accordion-item subject-accordion">
                {/* Subject Header */}
                <div
                  className="accordion-header"
                  onClick={() => toggleSubject(subject.id)}
                >
                  <div className="header-left">
                    <span className="accordion-icon">
                      {isSubjectExpanded ? '▼' : '▶'}
                    </span>
                    <div className="header-info">
                      <h2 className="subject-name">{subject.name}</h2>
                      <p className="subject-details">
                        <span className="subject-code">{subject.code}</span>
                        <span className="subject-separator">•</span>
                        <span>{subject.course.name}</span>
                        <span className="subject-separator">•</span>
                        <span>Semester {subject.semester}</span>
                      </p>
                    </div>
                  </div>
                  <div className="header-right">
                    <span className="batch-count">
                      {Object.keys(batches).length} Batch{Object.keys(batches).length !== 1 ? 'es' : ''}
                    </span>
                  </div>
                </div>

                {/* Subject Content - Batches */}
                {isSubjectExpanded && (
                  <div className="accordion-content">
                    {Object.entries(batches).map(([batchString, batchData]) => {
                      const batchKey = `${subject.id}-${batchString}`;
                      const isBatchExpanded = expandedBatches[batchKey];
                      
                      // Group students by branch
                      const branchGroups = groupStudentsByBranch(batchData.students);

                      return (
                        <div key={batchString} className="accordion-item batch-accordion">
                          {/* Batch Header */}
                          <div
                            className="accordion-header batch-header"
                            onClick={() => toggleBatch(subject.id, batchString)}
                          >
                            <div className="header-left">
                              <span className="accordion-icon">
                                {isBatchExpanded ? '▼' : '▶'}
                              </span>
                              <div className="header-info">
                                <h3 className="batch-name">Batch {batchString}</h3>
                                <p className="batch-stats">
                                  {batchData.students.length} Students • 
                                  Avg: <span className={getAttendanceColorClass(batchData.batch_average)}>
                                    {batchData.batch_average}%
                                  </span>
                                </p>
                              </div>
                            </div>
                            <div className="header-right">
                              <span className="branch-count">
                                {Object.keys(branchGroups).length} Branch{Object.keys(branchGroups).length !== 1 ? 'es' : ''}
                              </span>
                            </div>
                          </div>

                          {/* Batch Content - Branches */}
                          {isBatchExpanded && (
                            <div className="accordion-content">
                              {Object.entries(branchGroups).map(([branchCode, branchStudents]) => {
                                const branchKey = `${subject.id}-${batchString}-${branchCode}`;
                                const isBranchExpanded = expandedBranches[branchKey];
                                const reportKey = `${subject.id}-${batchString}-${branchCode}`;
                                const isSubmitted = submittedReports[reportKey];
                                const isSubmitting = submittingReports[reportKey];

                                // Calculate branch average
                                const branchAverage = branchStudents.length > 0
                                  ? branchStudents.reduce((sum, s) => sum + s.attendance_percentage, 0) / branchStudents.length
                                  : 0;

                                return (
                                  <div key={branchCode} className="accordion-item branch-accordion">
                                    {/* Branch Header */}
                                    <div
                                      className="accordion-header branch-header"
                                      onClick={() => toggleBranch(subject.id, batchString, branchCode)}
                                    >
                                      <div className="header-left">
                                        <span className="accordion-icon">
                                          {isBranchExpanded ? '▼' : '▶'}
                                        </span>
                                        <div className="header-info">
                                          <h4 className="branch-name">Branch: {branchCode}</h4>
                                          <p className="branch-stats">
                                            {branchStudents.length} Students • 
                                            Avg: <span className={getAttendanceColorClass(branchAverage)}>
                                              {branchAverage.toFixed(2)}%
                                            </span>
                                          </p>
                                        </div>
                                      </div>
                                    </div>

                                    {/* Branch Content - Student Table */}
                                    {isBranchExpanded && (
                                      <div className="accordion-content branch-content">
                                        <div className="students-table-container">
                                          <table className="students-table">
                                            <thead>
                                              <tr>
                                                <th>Reg No.</th>
                                                <th>Student Name</th>
                                                <th>Total Classes</th>
                                                <th>Attended</th>
                                                <th>Attendance %</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {branchStudents.map((student) => (
                                                <tr key={student.student_id}>
                                                  <td className="student-reg-no">{student.reg_no}</td>
                                                  <td className="student-name">{student.name}</td>
                                                  <td className="student-total">{student.total_classes}</td>
                                                  <td className="student-attended">{student.attended}</td>
                                                  <td className="student-percentage">
                                                    <span className={`percentage-badge ${getAttendanceColorClass(student.attendance_percentage)}`}>
                                                      {student.attendance_percentage}%
                                                    </span>
                                                  </td>
                                                </tr>
                                              ))}
                                            </tbody>
                                          </table>
                                        </div>

                                        {/* Submit Report Button */}
                                        <div className="branch-actions">
                                          <button
                                            className={`submit-report-btn ${isSubmitted ? 'submitted' : ''} ${isSubmitting ? 'submitting' : ''}`}
                                            onClick={() => handleSubmitReport(subject.id, batchString, branchCode)}
                                            disabled={isSubmitted || isSubmitting}
                                          >
                                            {isSubmitting ? (
                                              <>
                                                <span className="btn-spinner"></span>
                                                Sending...
                                              </>
                                            ) : isSubmitted ? (
                                              <>
                                                Report Sent to Admin
                                              </>
                                            ) : (
                                              <>
                                                Send Report to Admin
                                              </>
                                            )}
                                          </button>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            No attendance data available
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Attendance records will appear here once you start marking attendance for your subjects
          </p>
        </div>
      )}
    </div>
  );
};

export default FacultyAttendance;
