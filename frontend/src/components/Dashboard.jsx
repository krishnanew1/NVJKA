import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tokenUtils } from '../api';
import './Dashboard.css';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    if (!tokenUtils.isAuthenticated()) {
      navigate('/');
      return;
    }

    // For now, we'll just show a welcome message
    // In a real app, you'd decode the JWT token to get user info
    setUser({ username: 'User' });
  }, [navigate]);

  const handleLogout = () => {
    tokenUtils.clearTokens();
    navigate('/');
  };

  if (!user) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Academic ERP Dashboard</h1>
          <div className="header-actions">
            <span className="welcome-text">Welcome, {user.username}!</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h2>Authentication Successful!</h2>
            <p>You have successfully logged into the Academic ERP system.</p>
            <p>This is Phase 1 of the frontend development.</p>
          </div>

          <div className="next-steps">
            <h3>Coming Soon:</h3>
            <ul>
              <li>📊 Academic Management Dashboard</li>
              <li>👥 Student & Faculty Management</li>
              <li>📅 Timetable Generation & Viewing</li>
              <li>📝 Attendance Management</li>
              <li>📈 Grade & Transcript Management</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;