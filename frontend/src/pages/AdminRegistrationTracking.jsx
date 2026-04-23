import { useState } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const AdminRegistrationTracking = () => {
  // State management
  const [trackingData, setTrackingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [trackingForm, setTrackingForm] = useState({
    academic_year: '2025-26',
    semester: 'Jan-Jun 2026'
  });

  // Semester and academic year options (same as StudentRegistration)
  const semesterOptions = [
    { value: 'Jan-Jun 2026', label: 'Jan-Jun 2026' },
    { value: 'Jul-Dec 2026', label: 'Jul-Dec 2026' },
    { value: 'Jan-Jun 2027', label: 'Jan-Jun 2027' },
    { value: 'Jul-Dec 2027', label: 'Jul-Dec 2027' }
  ];

  const academicYearOptions = [
    { value: '2025-26', label: '2025-26' },
    { value: '2026-27', label: '2026-27' },
    { value: '2027-28', label: '2027-28' }
  ];

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Toast helpers
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Form handlers
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTrackingForm(prev => ({ ...prev, [name]: value }));
  };

  // Registration tracking functions
  const fetchRegistrationTracking = async () => {
    if (!trackingForm.academic_year || !trackingForm.semester) {
      showToast('Please select both academic year and semester', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get('/api/students/registration-tracking/', {
        params: {
          academic_year: trackingForm.academic_year,
          semester: trackingForm.semester
        }
      });
      setTrackingData(response.data);
      showToast('Registration tracking data loaded successfully', 'success');
    } catch (err) {
      console.error('Error fetching registration tracking:', err);
      const errorMsg = err.response?.data?.error || 'Failed to load registration tracking data';
      showToast(errorMsg, 'error');
      setTrackingData(null);
    } finally {
      setLoading(false);
    }
  };

  // Group students by registration status
  const groupStudentsByStatus = () => {
    if (!trackingData) return { registered: [], pending: [] };
    
    const registered = trackingData.students.filter(student => student.has_registered);
    const pending = trackingData.students.filter(student => !student.has_registered);
    
    return { registered, pending };
  };

  const { registered, pending } = groupStudentsByStatus();

  return (
    <div className="admin-dashboard">
      <Toast 
        message={toast.message} 
        type={toast.type} 
        isVisible={toast.isVisible} 
        onClose={hideToast} 
      />

      <div className="dashboard-header">
        <h1>Registration Tracking</h1>
        <p>Monitor semester registration progress across all students</p>
      </div>

      {/* Selection Controls */}
      <div className="tables-section">
        <div className="table-card" style={{ gridColumn: '1 / -1' }}>
          <div className="table-header">
            <h2>Select Semester to Track</h2>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <select
                name="academic_year"
                value={trackingForm.academic_year}
                onChange={handleInputChange}
                className="form-input"
                style={{ minWidth: '120px' }}
              >
                <option value="">Select Academic Year</option>
                {academicYearOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <select
                name="semester"
                value={trackingForm.semester}
                onChange={handleInputChange}
                className="form-input"
                style={{ minWidth: '150px' }}
              >
                <option value="">Select Semester</option>
                {semesterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button 
                className="add-btn" 
                onClick={fetchRegistrationTracking}
                disabled={loading || !trackingForm.academic_year || !trackingForm.semester}
              >
                {loading ? 'Loading...' : 'Track Registrations'}
              </button>
            </div>
          </div>

          {!trackingData && !loading && (
            <div className="empty-state" style={{ padding: '60px', textAlign: 'center' }}>
              <div className="empty-icon" style={{ fontSize: '64px', marginBottom: '20px' }}>📊</div>
              <h3 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-primary)' }}>
                Registration Tracking Dashboard
              </h3>
              <p style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '500px', margin: '0 auto 32px' }}>
                Select an academic year and semester to view detailed registration statistics and track which students have completed their semester registration.
              </p>
            </div>
          )}

          {loading && (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <Loader message="Loading registration data..." size="large" />
            </div>
          )}
        </div>
      </div>

      {/* Summary Statistics */}
      {trackingData && (
        <div className="summary-section">
          <div className="summary-card">
            <div className="card-icon" style={{ fontSize: '48px' }}>👥</div>
            <div className="card-content">
              <h3 className="card-number">{trackingData.summary.total_students}</h3>
              <p className="card-label">Total Students</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon" style={{ fontSize: '48px' }}>✅</div>
            <div className="card-content">
              <h3 className="card-number" style={{ color: 'var(--success-color)' }}>
                {trackingData.summary.registered}
              </h3>
              <p className="card-label">Registered</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon" style={{ fontSize: '48px' }}>⏳</div>
            <div className="card-content">
              <h3 className="card-number" style={{ color: 'var(--warning-color)' }}>
                {trackingData.summary.pending}
              </h3>
              <p className="card-label">Pending</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon" style={{ fontSize: '48px' }}>📈</div>
            <div className="card-content">
              <h3 className="card-number" style={{ color: 'var(--info-color)' }}>
                {trackingData.summary.registration_percentage}%
              </h3>
              <p className="card-label">Completion Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Registration Data */}
      {trackingData && (
        <div className="tables-section">
          <div className="table-card" style={{ gridColumn: '1 / -1' }}>
            <div className="table-header">
              <h2>Registration Details for {trackingData.academic_year} - {trackingData.semester}</h2>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <span style={{ 
                  padding: '6px 12px', 
                  backgroundColor: 'var(--success-light)', 
                  color: 'var(--success-color)',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {registered.length} Registered
                </span>
                <span style={{ 
                  padding: '6px 12px', 
                  backgroundColor: 'var(--warning-light)', 
                  color: 'var(--warning-color)',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {pending.length} Pending
                </span>
              </div>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Reg No</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Program</th>
                    <th>Department</th>
                    <th>Current Semester</th>
                    <th>Batch Year</th>
                    <th>Registration Status</th>
                    <th>Registration Date</th>
                  </tr>
                </thead>
                <tbody>
                  {trackingData.students.map(student => (
                    <tr key={student.id}>
                      <td className="table-code">{student.reg_no}</td>
                      <td className="table-name">{student.name}</td>
                      <td>{student.email}</td>
                      <td>{student.program.name}</td>
                      <td>{student.department.name}</td>
                      <td>{student.current_semester}</td>
                      <td>{student.batch_year}</td>
                      <td>
                        <span className={`status-badge ${student.has_registered ? 'status-success' : 'status-warning'}`}>
                          {student.has_registered ? '✅ Registered' : '⏳ Pending'}
                        </span>
                      </td>
                      <td>
                        {student.registration_date 
                          ? new Date(student.registration_date).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            })
                          : '-'
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Registration Progress by Program */}
      {trackingData && trackingData.students.length > 0 && (
        <div className="tables-section">
          <div className="table-card" style={{ gridColumn: '1 / -1' }}>
            <div className="table-header">
              <h2>Registration Progress by Program</h2>
            </div>
            
            <div className="table-container">
              {(() => {
                // Group students by program
                const programStats = {};
                trackingData.students.forEach(student => {
                  const programName = student.program.name;
                  if (!programStats[programName]) {
                    programStats[programName] = {
                      total: 0,
                      registered: 0,
                      pending: 0
                    };
                  }
                  programStats[programName].total++;
                  if (student.has_registered) {
                    programStats[programName].registered++;
                  } else {
                    programStats[programName].pending++;
                  }
                });

                return (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Program</th>
                        <th>Total Students</th>
                        <th>Registered</th>
                        <th>Pending</th>
                        <th>Completion Rate</th>
                        <th>Progress</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(programStats).map(([programName, stats]) => {
                        const completionRate = ((stats.registered / stats.total) * 100).toFixed(1);
                        return (
                          <tr key={programName}>
                            <td className="table-name">{programName}</td>
                            <td>{stats.total}</td>
                            <td style={{ color: 'var(--success-color)', fontWeight: '600' }}>
                              {stats.registered}
                            </td>
                            <td style={{ color: 'var(--warning-color)', fontWeight: '600' }}>
                              {stats.pending}
                            </td>
                            <td>
                              <span style={{ 
                                color: completionRate >= 80 ? 'var(--success-color)' : 
                                       completionRate >= 50 ? 'var(--warning-color)' : 'var(--danger-color)',
                                fontWeight: '600'
                              }}>
                                {completionRate}%
                              </span>
                            </td>
                            <td>
                              <div style={{ 
                                width: '100px', 
                                height: '8px', 
                                backgroundColor: 'var(--bg-secondary)', 
                                borderRadius: '4px',
                                overflow: 'hidden'
                              }}>
                                <div style={{ 
                                  width: `${completionRate}%`, 
                                  height: '100%', 
                                  backgroundColor: completionRate >= 80 ? 'var(--success-color)' : 
                                                 completionRate >= 50 ? 'var(--warning-color)' : 'var(--danger-color)',
                                  transition: 'width 0.3s ease'
                                }}></div>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminRegistrationTracking;