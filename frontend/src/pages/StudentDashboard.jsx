import './Dashboard.css';

const StudentDashboard = () => {
  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Student Dashboard</h1>
        <p>Welcome to your Student Portal</p>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">📚</div>
            <div className="card-content">
              <h3>My Courses</h3>
              <p>View your enrolled courses and subjects</p>
            </div>
          </div>
          
          <div className="dashboard-card">
            <div className="card-icon">📅</div>
            <div className="card-content">
              <h3>My Timetable</h3>
              <p>Check your weekly class schedule</p>
            </div>
          </div>
          
          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <h3>My Transcript</h3>
              <p>View grades, GPA, and academic progress</p>
            </div>
          </div>
          
          <div className="dashboard-card">
            <div className="card-icon">📋</div>
            <div className="card-content">
              <h3>Attendance</h3>
              <p>Track your attendance across all subjects</p>
            </div>
          </div>
        </div>
        
        <div className="dashboard-info">
          <div className="info-box">
            <h3>👨‍🎓 Student Portal</h3>
            <p>Access your academic information and track your progress.</p>
            <p><strong>Coming Soon:</strong> Interactive timetable and detailed transcript view</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;