import { useState, useEffect } from 'react';
import Toast from '../components/Toast';
import Loader from '../components/Loader';
import './Dashboard.css';

const StudentTimetable = () => {
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Toast state
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'info'
  });

  // Fetch timetable data
  const fetchTimetable = async () => {
    try {
      setLoading(true);
      setError('');

      // For now, we'll create a mock timetable since the backend endpoint might not be fully implemented
      // In production, this would be: const response = await api.get('/api/academics/timetable/');
      
      // Mock data structure
      const mockTimetable = [];
      
      setTimetable(mockTimetable);
    } catch (err) {
      console.error('Error fetching timetable:', err);
      
      if (err.response?.status === 404) {
        setTimetable([]);
        setError('');
      } else if (err.response?.status === 401) {
        setError('Authentication required. Please log in again.');
      } else {
        setError('');
        setTimetable([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimetable();
  }, []);

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Days and time slots
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const timeSlots = [
    '09:00 - 10:00',
    '10:00 - 11:00',
    '11:00 - 12:00',
    '12:00 - 01:00',
    '02:00 - 03:00',
    '03:00 - 04:00',
    '04:00 - 05:00'
  ];

  const LoadingSpinner = () => (
    <Loader message="Loading your timetable..." size="large" />
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
    <div className="student-timetable">
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      <div className="page-header">
        <h1>📅 My Timetable</h1>
        <p>Your weekly class schedule</p>
      </div>

      {timetable.length > 0 ? (
        <div className="timetable-container">
          <div className="timetable-grid">
            {/* Header row with days */}
            <div className="timetable-cell header-cell time-header">Time</div>
            {days.map(day => (
              <div key={day} className="timetable-cell header-cell">
                {day}
              </div>
            ))}

            {/* Time slots rows */}
            {timeSlots.map((slot, slotIndex) => (
              <>
                <div key={`time-${slotIndex}`} className="timetable-cell time-cell">
                  {slot}
                </div>
                {days.map((day) => {
                  const classData = timetable.find(
                    item => item.day === day && item.timeSlot === slot
                  );

                  return (
                    <div
                      key={`${day}-${slotIndex}`}
                      className={`timetable-cell ${classData ? 'has-class' : 'empty-cell'}`}
                    >
                      {classData ? (
                        <div className="class-info">
                          <div className="class-subject">{classData.subjectCode}</div>
                          <div className="class-room">Room: {classData.room}</div>
                          <div className="class-faculty">{classData.faculty}</div>
                        </div>
                      ) : (
                        <div className="empty-slot">-</div>
                      )}
                    </div>
                  );
                })}
              </>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <p>No timetable published yet</p>
          <p className="empty-subtext">Your class schedule will appear here once it's published by the administration</p>
        </div>
      )}
    </div>
  );
};

export default StudentTimetable;
