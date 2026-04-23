import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './StudentRegistration.css';

const StudentRegistration = () => {
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    academic_year: '',
    semester: '',
    institute_fee_paid: false,
    hostel_fee_paid: false,
    hostel_room_no: '',
    total_credits: 0
  });

  // Semester options
  const semesterOptions = [
    { value: 'Jan-Jun 2026', label: 'Jan-Jun 2026' },
    { value: 'Jul-Dec 2026', label: 'Jul-Dec 2026' },
    { value: 'Jan-Jun 2027', label: 'Jan-Jun 2027' },
    { value: 'Jul-Dec 2027', label: 'Jul-Dec 2027' }
  ];

  // Academic year options
  const academicYearOptions = [
    { value: '2025-26', label: '2025-26' },
    { value: '2026-27', label: '2026-27' },
    { value: '2027-28', label: '2027-28' }
  ];

  // Fee transactions state (max 3)
  const [feeTransactions, setFeeTransactions] = useState([]);
  const [receiptFiles, setReceiptFiles] = useState({});

  // Available subjects and selected courses
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [backlogCourses, setBacklogCourses] = useState([]);

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch available subjects
  useEffect(() => {
    fetchAvailableSubjects();
  }, []);

  const fetchAvailableSubjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/academics/subjects/');
      const subjects = response.data.results || response.data || [];
      setAvailableSubjects(subjects);
    } catch (err) {
      console.error('Error fetching subjects:', err);
      showToast('Failed to load subjects', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Toast helper
  const showToast = (message, type = 'info') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Add fee transaction
  const addFeeTransaction = () => {
    if (feeTransactions.length >= 3) {
      showToast('Maximum 3 fee transactions allowed', 'warning');
      return;
    }
    setFeeTransactions(prev => [...prev, {
      utr_no: '',
      bank_name: '',
      transaction_date: '',
      amount: '',
      account_debited: '',
      account_credited: ''
    }]);
  };

  // Remove fee transaction
  const removeFeeTransaction = (index) => {
    setFeeTransactions(prev => prev.filter((_, i) => i !== index));
  };

  // Update fee transaction
  const updateFeeTransaction = (index, field, value) => {
    setFeeTransactions(prev => prev.map((txn, i) => 
      i === index ? { ...txn, [field]: value } : txn
    ));
  };

  // Handle receipt file upload
  const handleReceiptUpload = (index, file) => {
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
      if (!validTypes.includes(file.type)) {
        showToast('Please upload a valid image (JPG, PNG) or PDF file', 'error');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        showToast('File size should not exceed 5MB', 'error');
        return;
      }
      
      setReceiptFiles(prev => ({ ...prev, [index]: file }));
      showToast('Receipt uploaded successfully', 'success');
    }
  };

  // Toggle course selection
  const toggleCourseSelection = (subject, isBacklog = false) => {
    if (isBacklog) {
      setBacklogCourses(prev => {
        const exists = prev.find(c => c.id === subject.id);
        if (exists) {
          return prev.filter(c => c.id !== subject.id);
        }
        return [...prev, subject];
      });
    } else {
      setSelectedCourses(prev => {
        const exists = prev.find(c => c.id === subject.id);
        if (exists) {
          return prev.filter(c => c.id !== subject.id);
        }
        return [...prev, subject];
      });
    }
  };

  // Check if course is selected
  const isCourseSelected = (subjectId, isBacklog = false) => {
    const list = isBacklog ? backlogCourses : selectedCourses;
    return list.some(c => c.id === subjectId);
  };

  // Calculate total credits
  const calculateTotalCredits = () => {
    const currentCredits = selectedCourses.reduce((sum, course) => sum + (course.credits || 0), 0);
    const backlogCredits = backlogCourses.reduce((sum, course) => sum + (course.credits || 0), 0);
    return currentCredits + backlogCredits;
  };

  const totalCredits = calculateTotalCredits();
  const isCreditsExceeded = totalCredits > 32;

  // Validate form
  const validateForm = () => {
    if (!formData.academic_year.trim()) {
      showToast('Please enter academic year', 'error');
      return false;
    }
    if (!formData.semester.trim()) {
      showToast('Please enter semester', 'error');
      return false;
    }
    if (selectedCourses.length === 0 && backlogCourses.length === 0) {
      showToast('Please select at least one course', 'error');
      return false;
    }
    if (isCreditsExceeded) {
      showToast('Total credits cannot exceed 32', 'error');
      return false;
    }
    return true;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      setSubmitting(true);

      // Prepare registered courses
      const registered_courses = [
        ...selectedCourses.map(course => ({
          subject_id: course.id,
          is_backlog: false
        })),
        ...backlogCourses.map(course => ({
          subject_id: course.id,
          is_backlog: true
        }))
      ];

      // Prepare fee transactions
      const fee_transactions = feeTransactions
        .filter(txn => txn.utr_no && txn.bank_name && txn.transaction_date && txn.amount)
        .map(txn => ({
          utr_no: txn.utr_no,
          bank_name: txn.bank_name,
          transaction_date: txn.transaction_date,
          amount: parseFloat(txn.amount),
          account_debited: txn.account_debited,
          account_credited: txn.account_credited
        }));

      // Check if we have any file uploads
      const hasFileUploads = Object.keys(receiptFiles).length > 0;

      if (hasFileUploads) {
        // Use FormData for file uploads
        const submitData = new FormData();
        submitData.append('academic_year', formData.academic_year);
        submitData.append('semester', formData.semester);
        submitData.append('institute_fee_paid', formData.institute_fee_paid);
        submitData.append('hostel_fee_paid', formData.hostel_fee_paid);
        if (formData.hostel_room_no) submitData.append('hostel_room_no', formData.hostel_room_no);
        submitData.append('total_credits', totalCredits);

        // Add fee transactions with receipts
        fee_transactions.forEach((txn, index) => {
          Object.keys(txn).forEach(key => {
            submitData.append(`fee_transactions[${index}][${key}]`, txn[key]);
          });
          
          // Add receipt file if uploaded
          if (receiptFiles[index]) {
            submitData.append(`fee_transactions[${index}][receipt_image]`, receiptFiles[index]);
          }
        });

        // Add registered courses
        registered_courses.forEach((course, index) => {
          submitData.append(`registered_courses[${index}][subject_id]`, course.subject_id);
          submitData.append(`registered_courses[${index}][is_backlog]`, course.is_backlog);
        });

        await api.post('/api/students/semester-register/', submitData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        // Use JSON for simpler data without files
        const submitData = {
          academic_year: formData.academic_year,
          semester: formData.semester,
          institute_fee_paid: formData.institute_fee_paid,
          hostel_fee_paid: formData.hostel_fee_paid,
          hostel_room_no: formData.hostel_room_no || null,
          total_credits: totalCredits,
          fee_transactions: fee_transactions,
          registered_courses: registered_courses
        };

        await api.post('/api/students/semester-register/', submitData, {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      showToast('Semester registration successful!', 'success');
      
      // Redirect to dashboard after 1.5 seconds
      setTimeout(() => {
        navigate('/student');
      }, 1500);

    } catch (err) {
      console.error('Error submitting registration:', err);
      
      // Handle different types of errors
      let errorMessage = 'Failed to submit registration. Please try again.';
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Handle validation errors
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (typeof errorData === 'object') {
          // Check for common error fields in order of priority
          if (errorData.detail && typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.message && typeof errorData.message === 'string') {
            errorMessage = errorData.message;
          } else if (errorData.non_field_errors) {
            if (Array.isArray(errorData.non_field_errors)) {
              errorMessage = errorData.non_field_errors.join(', ');
            } else if (typeof errorData.non_field_errors === 'string') {
              errorMessage = errorData.non_field_errors;
            } else {
              errorMessage = 'Validation error occurred.';
            }
          } else {
            // Handle field-specific errors
            const fieldErrors = [];
            Object.keys(errorData).forEach(field => {
              const fieldValue = errorData[field];
              if (Array.isArray(fieldValue)) {
                fieldErrors.push(`${field}: ${fieldValue.join(', ')}`);
              } else if (typeof fieldValue === 'string') {
                fieldErrors.push(`${field}: ${fieldValue}`);
              } else if (typeof fieldValue === 'object' && fieldValue !== null) {
                // Handle nested error objects
                fieldErrors.push(`${field}: ${JSON.stringify(fieldValue)}`);
              }
            });
            if (fieldErrors.length > 0) {
              errorMessage = fieldErrors.join('; ');
            }
          }
        }
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  // Group subjects by semester
  const groupSubjectsBySemester = () => {
    const grouped = {};
    availableSubjects.forEach(subject => {
      const sem = subject.semester || 'Other';
      if (!grouped[sem]) {
        grouped[sem] = [];
      }
      grouped[sem].push(subject);
    });
    return grouped;
  };

  const groupedSubjects = groupSubjectsBySemester();

  if (loading) {
    return <Loader message="Loading registration form..." size="large" />;
  }

  return (
    <div className="student-registration">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Page Header */}
      <div className="registration-header">
        <div className="header-content">
          <h1 className="page-title">Semester Registration</h1>
          <p className="page-subtitle">Register for the upcoming semester</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="registration-form">
        {/* Section 1: Academic Information */}
        <div className="form-section">
          <div className="section-header">
            <h2 className="section-title">Academic Information</h2>
            <p className="section-subtitle">Enter semester details</p>
          </div>
          
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="academic_year" className="form-label">
                Academic Year <span className="required">*</span>
              </label>
              <select
                id="academic_year"
                name="academic_year"
                value={formData.academic_year}
                onChange={handleInputChange}
                className="form-input"
                required
              >
                <option value="">Select Academic Year</option>
                {academicYearOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="semester" className="form-label">
                Semester <span className="required">*</span>
              </label>
              <select
                id="semester"
                name="semester"
                value={formData.semester}
                onChange={handleInputChange}
                className="form-input"
                required
              >
                <option value="">Select Semester</option>
                {semesterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="institute_fee_paid"
                  checked={formData.institute_fee_paid}
                  onChange={handleInputChange}
                  className="form-checkbox"
                />
                <span className="checkbox-text">Institute Fee Paid</span>
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="hostel_fee_paid"
                  checked={formData.hostel_fee_paid}
                  onChange={handleInputChange}
                  className="form-checkbox"
                />
                <span className="checkbox-text">Hostel Fee Paid</span>
              </label>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="hostel_room_no" className="form-label">
              Hostel Room Number
            </label>
            <input
              type="text"
              id="hostel_room_no"
              name="hostel_room_no"
              value={formData.hostel_room_no}
              onChange={handleInputChange}
              placeholder="e.g., BH-101"
              className="form-input"
            />
          </div>
        </div>

        {/* Section 2: Fee Details */}
        <div className="form-section">
          <div className="section-header">
            <h2 className="section-title">Fee Transaction Details</h2>
            <p className="section-subtitle">Add up to 3 fee transactions (optional)</p>
          </div>

          {feeTransactions.map((txn, index) => (
            <div key={index} className="fee-transaction-card">
              <div className="transaction-header">
                <h3 className="transaction-title">Transaction {index + 1}</h3>
                <button
                  type="button"
                  onClick={() => removeFeeTransaction(index)}
                  className="remove-transaction-btn"
                >
                  ✕ Remove
                </button>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">UTR Number</label>
                  <input
                    type="text"
                    value={txn.utr_no}
                    onChange={(e) => updateFeeTransaction(index, 'utr_no', e.target.value)}
                    placeholder="Enter UTR number"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Bank Name</label>
                  <input
                    type="text"
                    value={txn.bank_name}
                    onChange={(e) => updateFeeTransaction(index, 'bank_name', e.target.value)}
                    placeholder="Enter bank name"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Transaction Date</label>
                  <input
                    type="date"
                    value={txn.transaction_date}
                    onChange={(e) => updateFeeTransaction(index, 'transaction_date', e.target.value)}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Amount</label>
                  <input
                    type="number"
                    value={txn.amount}
                    onChange={(e) => updateFeeTransaction(index, 'amount', e.target.value)}
                    placeholder="Enter amount"
                    className="form-input"
                    min="0"
                    step="0.01"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Account Debited</label>
                  <input
                    type="text"
                    value={txn.account_debited}
                    onChange={(e) => updateFeeTransaction(index, 'account_debited', e.target.value)}
                    placeholder="Your account"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Account Credited</label>
                  <input
                    type="text"
                    value={txn.account_credited}
                    onChange={(e) => updateFeeTransaction(index, 'account_credited', e.target.value)}
                    placeholder="Institute account"
                    className="form-input"
                  />
                </div>

                <div className="form-group full-width">
                  <label className="form-label">
                    Fee Receipt Screenshot <span className="required">*</span>
                  </label>
                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,application/pdf"
                    onChange={(e) => handleReceiptUpload(index, e.target.files[0])}
                    className="form-input file-input"
                  />
                  {receiptFiles[index] && (
                    <div className="file-preview">
                      <span className="file-name">📄 {receiptFiles[index].name}</span>
                      <span className="file-size">({(receiptFiles[index].size / 1024 / 1024).toFixed(2)} MB)</span>
                    </div>
                  )}
                  <small className="form-hint">
                    Upload fee receipt (JPG, PNG, or PDF - Max 5MB)
                    {receiptFiles[index] && (
                      <span className="file-uploaded"> ✓ {receiptFiles[index].name}</span>
                    )}
                  </small>
                </div>
              </div>
            </div>
          ))}

          {feeTransactions.length < 3 && (
            <button
              type="button"
              onClick={addFeeTransaction}
              className="add-transaction-btn"
            >
              + Add Fee Transaction
            </button>
          )}
        </div>

        {/* Section 3: Course Selection */}
        <div className="form-section">
          <div className="section-header">
            <h2 className="section-title">Course Selection</h2>
            <p className="section-subtitle">Select courses for this semester</p>
          </div>

          {/* Credits Summary */}
          <div className={`credits-summary ${isCreditsExceeded ? 'credits-exceeded' : ''}`}>
            <div className="credits-info">
              <span className="credits-label">Total Credits:</span>
              <span className="credits-value">{totalCredits} / 32</span>
            </div>
            {isCreditsExceeded && (
              <div className="credits-warning">
                ⚠️ Total Credits including backlog courses should not be greater than 32
              </div>
            )}
          </div>

          {/* Current Semester Courses */}
          <div className="courses-subsection">
            <h3 className="subsection-title">Current Semester Courses</h3>
            {Object.keys(groupedSubjects).length > 0 ? (
              <div className="courses-table-container">
                <table className="courses-table">
                  <thead>
                    <tr>
                      <th>Select</th>
                      <th>Course Code</th>
                      <th>Course Name</th>
                      <th>Credits</th>
                      <th>Semester</th>
                    </tr>
                  </thead>
                  <tbody>
                    {availableSubjects.map(subject => (
                      <tr key={subject.id}>
                        <td>
                          <input
                            type="checkbox"
                            checked={isCourseSelected(subject.id, false)}
                            onChange={() => toggleCourseSelection(subject, false)}
                            className="course-checkbox"
                          />
                        </td>
                        <td className="course-code">{subject.code}</td>
                        <td className="course-name">{subject.name}</td>
                        <td className="course-credits">{subject.credits}</td>
                        <td className="course-semester">Sem {subject.semester}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon"></div>
                <p>No courses available</p>
              </div>
            )}
          </div>

          {/* Backlog Courses */}
          <div className="courses-subsection">
            <h3 className="subsection-title">Backlog Courses</h3>
            {availableSubjects.length > 0 ? (
              <div className="courses-table-container">
                <table className="courses-table">
                  <thead>
                    <tr>
                      <th>Select</th>
                      <th>Course Code</th>
                      <th>Course Name</th>
                      <th>Credits</th>
                      <th>Semester</th>
                    </tr>
                  </thead>
                  <tbody>
                    {availableSubjects.map(subject => (
                      <tr key={`backlog-${subject.id}`}>
                        <td>
                          <input
                            type="checkbox"
                            checked={isCourseSelected(subject.id, true)}
                            onChange={() => toggleCourseSelection(subject, true)}
                            className="course-checkbox"
                          />
                        </td>
                        <td className="course-code">{subject.code}</td>
                        <td className="course-name">{subject.name}</td>
                        <td className="course-credits">{subject.credits}</td>
                        <td className="course-semester">Sem {subject.semester}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon"></div>
                <p>No backlog courses</p>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/student')}
            className="cancel-btn"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="submit-btn"
            disabled={submitting || isCreditsExceeded}
          >
            {submitting ? 'Submitting...' : 'Submit Registration'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StudentRegistration;
