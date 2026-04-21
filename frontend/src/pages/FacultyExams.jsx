import { useState, useEffect } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './FacultyExams.css';

const FacultyExams = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [students, setStudents] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [grades, setGrades] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch faculty's assigned subjects
  const fetchSubjects = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/academics/faculty/my-subjects/');
      const data = Array.isArray(response.data) ? response.data : response.data.results || [];
      
      setSubjects(data);
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

  // Grade options for dropdown - strict 10-point scale
  const gradeOptions = [
    { value: '', label: '-- Select Grade --' },
    { value: 'A', label: 'A (10)' },
    { value: 'A-', label: 'A- (9)' },
    { value: 'B', label: 'B (8)' },
    { value: 'B-', label: 'B- (7)' },
    { value: 'C', label: 'C (6)' },
    { value: 'C-', label: 'C- (5)' },
    { value: 'D', label: 'D (4)' },
    { value: 'F', label: 'Fail (0)' },
  ];

  // Handle subject selection
  const handleSubjectChange = async (e) => {
    const subjectId = e.target.value;
    
    if (!subjectId) {
      setSelectedSubject(null);
      setStudents([]);
      setGrades({});
      return;
    }

    const subject = subjects.find(s => s.id === parseInt(subjectId));
    setSelectedSubject(subject);

    // Fetch students for this subject
    await fetchStudentsForSubject(subject);
  };

  // Fetch students enrolled in the selected subject
  const fetchStudentsForSubject = async (subject) => {
    try {
      setLoadingStudents(true);

      const response = await api.get('/api/students/enrollments/', {
        params: {
          course: subject.course?.id,
          semester: subject.semester,
          status: 'Active'
        }
      });

      const enrollments = response.data.results || response.data;
      
      // Extract student profiles
      const studentProfiles = enrollments.map(enrollment => ({
        id: enrollment.student.id,
        name: enrollment.student.user?.full_name || enrollment.student.user?.username || 'Unknown',
        enrollment_number: enrollment.student.enrollment_number || 'N/A',
      }));

      setStudents(studentProfiles);

      // Initialize grades object with default values
      const initialGrades = {};
      studentProfiles.forEach(student => {
        initialGrades[student.id] = {
          marks_obtained: '',
          total_marks: 100,
          grade_letter: '', // Empty by default - faculty must select
          remarks: ''
        };
      });
      setGrades(initialGrades);

    } catch (err) {
      console.error('Error fetching students:', err);
      showToast('Failed to load students. Please try again.', 'error');
      setStudents([]);
    } finally {
      setLoadingStudents(false);
    }
  };

  // Handle grade input change
  const handleGradeChange = (studentId, field, value) => {
    setGrades(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [field]: value
      }
    }));
  };

  // Handle save grades
  const handleSaveGrades = async () => {
    if (!selectedSubject) {
      showToast('Please select a subject first.', 'warning');
      return;
    }

    // Validate that at least one complete grade is entered
    const gradesArray = Object.entries(grades)
      .filter(([_, grade]) => 
        grade.marks_obtained !== '' && 
        grade.total_marks !== '' && 
        grade.grade_letter !== ''
      )
      .map(([studentId, grade]) => ({
        student_id: parseInt(studentId),
        marks_obtained: parseFloat(grade.marks_obtained),
        total_marks: parseFloat(grade.total_marks),
        grade_letter: grade.grade_letter,
        remarks: grade.remarks
      }));

    if (gradesArray.length === 0) {
      showToast('Please enter complete grades (marks and grade letter) for at least one student.', 'warning');
      return;
    }

    // Validate marks
    const invalidGrades = gradesArray.filter(g => 
      g.marks_obtained < 0 || 
      g.total_marks <= 0 || 
      g.marks_obtained > g.total_marks
    );

    if (invalidGrades.length > 0) {
      showToast('Invalid marks detected. Please check your entries.', 'error');
      return;
    }

    // Validate that all entries have grade letters
    const missingGrades = gradesArray.filter(g => !g.grade_letter);
    if (missingGrades.length > 0) {
      showToast('Please select a grade letter for all students with marks entered.', 'warning');
      return;
    }

    try {
      setIsSaving(true);

      const payload = {
        subject_id: selectedSubject.id,
        grades: gradesArray
      };

      await api.post('/api/exams/faculty/grades/', payload);

      showToast(`Grades saved successfully for ${gradesArray.length} students!`, 'success');
      
      // Optionally refresh the data
      // await fetchStudentsForSubject(selectedSubject);

    } catch (err) {
      console.error('Error saving grades:', err);
      if (err.response?.status === 400) {
        showToast('Invalid data. Please check your entries.', 'error');
      } else if (err.response?.status === 403) {
        showToast('You are not authorized to submit grades for this subject.', 'error');
      } else {
        showToast('Failed to save grades. Please try again.', 'error');
      }
    } finally {
      setIsSaving(false);
    }
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

  return (
    <div className="faculty-exams">
      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="exams-header">
        <h1>Exams & Grades</h1>
        <p>Submit and manage student grades for your subjects</p>
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

      {/* Students Table */}
      {selectedSubject && (
        <div className="grades-table-card">
          <div className="card-header">
            <h2>Student Grades - {selectedSubject.name}</h2>
            <p>{students.length} students enrolled</p>
          </div>

          {loadingStudents ? (
            <div className="table-loading">
              <div className="spinner"></div>
              <p>Loading students...</p>
            </div>
          ) : students.length > 0 ? (
            <>
              <div className="table-container">
                <table className="grades-table">
                  <thead>
                    <tr>
                      <th>Enrollment No.</th>
                      <th>Student Name</th>
                      <th>Marks Obtained</th>
                      <th>Total Marks</th>
                      <th>Grade Letter</th>
                      <th>Remarks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map(student => (
                      <tr key={student.id}>
                        <td className="enrollment-cell">{student.enrollment_number}</td>
                        <td className="name-cell">{student.name}</td>
                        <td className="marks-cell">
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={grades[student.id]?.marks_obtained || ''}
                            onChange={(e) => handleGradeChange(student.id, 'marks_obtained', e.target.value)}
                            placeholder="0"
                            disabled={isSaving}
                          />
                        </td>
                        <td className="marks-cell">
                          <input
                            type="number"
                            min="1"
                            step="0.01"
                            value={grades[student.id]?.total_marks || 100}
                            onChange={(e) => handleGradeChange(student.id, 'total_marks', e.target.value)}
                            disabled={isSaving}
                          />
                        </td>
                        <td className="grade-cell">
                          <select
                            value={grades[student.id]?.grade_letter || ''}
                            onChange={(e) => handleGradeChange(student.id, 'grade_letter', e.target.value)}
                            disabled={isSaving}
                            className="grade-select"
                          >
                            {gradeOptions.map(option => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="remarks-cell">
                          <input
                            type="text"
                            value={grades[student.id]?.remarks || ''}
                            onChange={(e) => handleGradeChange(student.id, 'remarks', e.target.value)}
                            placeholder="Optional"
                            disabled={isSaving}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Save Button */}
              <div className="table-actions">
                <button
                  className={`save-grades-btn ${isSaving ? 'saving' : ''}`}
                  onClick={handleSaveGrades}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <span className="btn-spinner"></span>
                      Saving Grades...
                    </>
                  ) : (
                    <>
                      Save Grades
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon"></div>
              <p>No students enrolled in this subject</p>
            </div>
          )}
        </div>
      )}

      {/* Empty State - No Subject Selected */}
      {!selectedSubject && subjects.length > 0 && (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            Select a subject to begin
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Choose a subject from the dropdown above to view enrolled students and enter grades
          </p>
        </div>
      )}

      {/* Empty State - No Subjects */}
      {subjects.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            No subjects assigned
          </p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            You don't have any subjects assigned yet. Contact the administration for subject assignments.
          </p>
        </div>
      )}
    </div>
  );
};

export default FacultyExams;
