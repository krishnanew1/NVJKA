import { useState, useEffect } from 'react';
import api from '../api';
import Modal from '../components/Modal';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './AdminRegTracking.css';

const AdminRegTracking = () => {
  // Filter state
  const [academicYear, setAcademicYear] = useState('2025-26');
  const [semester, setSemester] = useState('Jan-Jun 2026');
  const [filterTab, setFilterTab] = useState('all'); // 'all', 'registered', 'pending'

  // Data state
  const [trackingData, setTrackingData] = useState(null);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [registrationDetail, setRegistrationDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch tracking data
  const fetchTrackingData = async () => {
    if (!academicYear || !semester) {
      showToast('Please select both academic year and semester', 'warning');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await api.get('/api/students/registration-tracking/', {
        params: {
          academic_year: academicYear,
          semester: semester
        }
      });

      setTrackingData(response.data);
      setFilteredStudents(response.data.students);
    } catch (err) {
      console.error('Error fetching tracking data:', err);
      const errorMessage = err.response?.data?.error || 
                          'Failed to load tracking data. Please try again.';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Fetch registration detail
  const fetchRegistrationDetail = async (studentId, registrationId) => {
    try {
      setLoadingDetail(true);

      const response = await api.get(
        `/api/students/registration-detail/${studentId}/${registrationId}/`
      );

      setRegistrationDetail(response.data);
    } catch (err) {
      console.error('Error fetching registration detail:', err);
      showToast('Failed to load registration details', 'error');
    } finally {
      setLoadingDetail(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchTrackingData();
  }, []);

  // Filter students based on tab
  useEffect(() => {
    if (!trackingData) return;

    let filtered = trackingData.students;

    if (filterTab === 'registered') {
      filtered = filtered.filter(s => s.has_registered);
    } else if (filterTab === 'pending') {
      filtered = filtered.filter(s => !s.has_registered);
    }

    setFilteredStudents(filtered);
  }, [filterTab, trackingData]);

  // Toast helper
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Handle view form
  const handleViewForm = async (student) => {
    setSelectedStudent(student);
    setIsModalOpen(true);
    await fetchRegistrationDetail(student.id, student.registration_id);
  };

  // Close modal
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedStudent(null);
    setRegistrationDetail(null);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  if (loading && !trackingData) {
    return <Loader message="Loading registration tracking data..." size="large" />;
  }

  return (
    <div className="admin-reg-tracking">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="tracking-header">
        <div className="header-content">
          <h1 className="page-title">Registration Tracking</h1>
          <p className="page-subtitle">Monitor semester registration status</p>
        </div>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <div className="filter-controls">
          <div className="filter-group">
            <label htmlFor="academic-year" className="filter-label">
              Academic Year
            </label>
            <input
              type="text"
              id="academic-year"
              value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)}
              placeholder="e.g., 2025-26"
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label htmlFor="semester" className="filter-label">
              Semester
            </label>
            <input
              type="text"
              id="semester"
              value={semester}
              onChange={(e) => setSemester(e.target.value)}
              placeholder="e.g., Jan-Jun 2026"
              className="filter-input"
            />
          </div>

          <button
            onClick={fetchTrackingData}
            className="fetch-btn"
            disabled={loading}
          >
            {loading ? 'Loading...' : '🔍 Fetch Data'}
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {trackingData && (
        <div className="summary-section">
          <div className="summary-card total">
            <div className="card-icon"></div>
            <div className="card-content">
              <div className="card-value">{trackingData.summary.total_students}</div>
              <div className="card-label">Total Students</div>
            </div>
          </div>

          <div className="summary-card registered">
            <div className="card-icon"></div>
            <div className="card-content">
              <div className="card-value">{trackingData.summary.registered}</div>
              <div className="card-label">Registered</div>
            </div>
          </div>

          <div className="summary-card pending">
            <div className="card-icon"></div>
            <div className="card-content">
              <div className="card-value">{trackingData.summary.pending}</div>
              <div className="card-label">Pending</div>
            </div>
          </div>

          <div className="summary-card percentage">
            <div className="card-icon"></div>
            <div className="card-content">
              <div className="card-value">{trackingData.summary.registration_percentage}%</div>
              <div className="card-label">Registration Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      {trackingData && (
        <div className="filter-tabs">
          <button
            className={`tab-btn ${filterTab === 'all' ? 'active' : ''}`}
            onClick={() => setFilterTab('all')}
          >
            All Students ({trackingData.students.length})
          </button>
          <button
            className={`tab-btn ${filterTab === 'registered' ? 'active' : ''}`}
            onClick={() => setFilterTab('registered')}
          >
            Registered ({trackingData.summary.registered})
          </button>
          <button
            className={`tab-btn ${filterTab === 'pending' ? 'active' : ''}`}
            onClick={() => setFilterTab('pending')}
          >
            Pending ({trackingData.summary.pending})
          </button>
        </div>
      )}

      {/* Data Table */}
      {trackingData && filteredStudents.length > 0 ? (
        <div className="data-table-section">
          <div className="table-container">
            <table className="tracking-table">
              <thead>
                <tr>
                  <th>Reg No</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Program</th>
                  <th>Department</th>
                  <th>Semester</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((student) => (
                  <tr key={student.id}>
                    <td className="reg-no">{student.reg_no}</td>
                    <td className="student-name">{student.name}</td>
                    <td className="student-email">{student.email}</td>
                    <td className="program-info">
                      <div className="program-name">{student.program.name}</div>
                      <div className="program-code">{student.program.code}</div>
                    </td>
                    <td className="department-code">{student.department.code}</td>
                    <td className="semester-info">{student.current_semester}</td>
                    <td className="status-cell">
                      {student.has_registered ? (
                        <span className="status-badge completed">
                          ✓ Completed
                        </span>
                      ) : (
                        <span className="status-badge pending">
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="action-cell">
                      {student.has_registered ? (
                        <button
                          onClick={() => handleViewForm(student)}
                          className="view-btn"
                        >
                          View Form
                        </button>
                      ) : (
                        <span className="no-action">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : trackingData && filteredStudents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <p>No students found for the selected filter</p>
        </div>
      ) : null}

      {/* Error State */}
      {error && !trackingData && (
        <div className="error-state">
          <div className="error-icon"></div>
          <p>{error}</p>
          <button onClick={fetchTrackingData} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {/* Verification Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={selectedStudent ? `Registration Details - ${selectedStudent.name}` : 'Registration Details'}
      >
        {loadingDetail ? (
          <div className="modal-loading">
            <Loader message="Loading details..." size="medium" />
          </div>
        ) : registrationDetail ? (
          <div className="registration-detail-modal">
            {/* Student Info */}
            <div className="detail-section">
              <h3 className="section-title">Student Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Reg No:</span>
                  <span className="info-value">{registrationDetail.student.reg_no}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Email:</span>
                  <span className="info-value">{registrationDetail.student.email}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Program:</span>
                  <span className="info-value">{registrationDetail.student.program.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Department:</span>
                  <span className="info-value">{registrationDetail.student.department.name}</span>
                </div>
              </div>
            </div>

            {/* Registration Info */}
            <div className="detail-section">
              <h3 className="section-title">Registration Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Academic Year:</span>
                  <span className="info-value">{registrationDetail.registration.academic_year}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Semester:</span>
                  <span className="info-value">{registrationDetail.registration.semester}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Institute Fee:</span>
                  <span className={`info-value ${registrationDetail.registration.institute_fee_paid ? 'paid' : 'unpaid'}`}>
                    {registrationDetail.registration.institute_fee_paid ? '✓ Paid' : '✗ Not Paid'}
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">Hostel Fee:</span>
                  <span className={`info-value ${registrationDetail.registration.hostel_fee_paid ? 'paid' : 'unpaid'}`}>
                    {registrationDetail.registration.hostel_fee_paid ? '✓ Paid' : '✗ Not Paid'}
                  </span>
                </div>
                {registrationDetail.registration.hostel_room_no && (
                  <div className="info-item">
                    <span className="info-label">Hostel Room:</span>
                    <span className="info-value">{registrationDetail.registration.hostel_room_no}</span>
                  </div>
                )}
                <div className="info-item">
                  <span className="info-label">Total Credits:</span>
                  <span className="info-value">{registrationDetail.registration.total_credits}</span>
                </div>
              </div>
            </div>

            {/* Fee Transactions */}
            <div className="detail-section">
              <h3 className="section-title">Fee Transactions ({registrationDetail.fee_transactions.length})</h3>
              {registrationDetail.fee_transactions.length > 0 ? (
                <div className="transactions-list">
                  {registrationDetail.fee_transactions.map((txn, index) => (
                    <div key={txn.id} className="transaction-card">
                      <div className="transaction-header">
                        <span className="transaction-number">Transaction {index + 1}</span>
                        <span className="transaction-amount">₹{parseFloat(txn.amount).toLocaleString()}</span>
                      </div>
                      <div className="transaction-details">
                        <div className="detail-row">
                          <span className="detail-label">UTR Number:</span>
                          <span className="detail-value utr">{txn.utr_no}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Bank:</span>
                          <span className="detail-value">{txn.bank_name}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Date:</span>
                          <span className="detail-value">{formatDate(txn.transaction_date)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Debited From:</span>
                          <span className="detail-value">{txn.account_debited}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Credited To:</span>
                          <span className="detail-value">{txn.account_credited}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">No fee transactions recorded</p>
              )}
            </div>

            {/* Registered Courses */}
            <div className="detail-section">
              <h3 className="section-title">Registered Courses ({registrationDetail.registered_courses.length})</h3>
              {registrationDetail.registered_courses.length > 0 ? (
                <div className="courses-table-container">
                  <table className="courses-table">
                    <thead>
                      <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Credits</th>
                        <th>Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {registrationDetail.registered_courses.map((course) => (
                        <tr key={course.id}>
                          <td className="course-code">{course.subject.code}</td>
                          <td className="course-name">{course.subject.name}</td>
                          <td className="course-credits">{course.subject.credits}</td>
                          <td className="course-type">
                            {course.is_backlog ? (
                              <span className="type-badge backlog">Backlog</span>
                            ) : (
                              <span className="type-badge current">Current</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="no-data">No courses registered</p>
              )}
            </div>

            {/* Summary */}
            <div className="detail-section summary-section-modal">
              <h3 className="section-title">Summary</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Total Fee Amount:</span>
                  <span className="summary-value">₹{parseFloat(registrationDetail.summary.total_fee_amount).toLocaleString()}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Courses:</span>
                  <span className="summary-value">{registrationDetail.summary.total_courses}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Current Courses:</span>
                  <span className="summary-value">{registrationDetail.summary.current_courses}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Backlog Courses:</span>
                  <span className="summary-value">{registrationDetail.summary.backlog_courses}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="modal-error">
            <p>Failed to load registration details</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AdminRegTracking;
