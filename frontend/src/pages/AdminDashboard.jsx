import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Loader from '../components/Loader';
import './Dashboard.css';

const AdminDashboard = () => {
  const navigate = useNavigate();
  
  // State management
  const [stats, setStats] = useState({
    departments: 0,
    courses: 0,
    students: 0,
    faculty: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Data fetching
  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch all stats in parallel
      const [departmentsRes, coursesRes, studentsRes, facultyRes] = await Promise.all([
        api.get('/api/academics/departments/'),
        api.get('/api/academics/courses/'),
        api.get('/api/users/students/'),
        api.get('/api/faculty/')
      ]);

      setStats({
        departments: (departmentsRes.data.results || departmentsRes.data).length,
        courses: (coursesRes.data.results || coursesRes.data).length,
        students: (studentsRes.data.results || studentsRes.data).length,
        faculty: (facultyRes.data.results || facultyRes.data).length
      });
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError('Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  if (loading) {
    return <Loader message="Loading dashboard..." size="large" />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <p className="error-text">{error}</p>
        <button onClick={fetchDashboardStats} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1>🎯 Admin Dashboard</h1>
        <p>Welcome back! Here's your system overview</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card" onClick={() => navigate('/admin/academics')}>
          <div className="stat-icon">🏛️</div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.departments}</h3>
            <p className="stat-label">Departments</p>
          </div>
        </div>

        <div className="stat-card" onClick={() => navigate('/admin/academics')}>
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.courses}</h3>
            <p className="stat-label">Courses</p>
          </div>
        </div>

        <div className="stat-card" onClick={() => navigate('/admin/students')}>
          <div className="stat-icon">👨‍🎓</div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.students}</h3>
            <p className="stat-label">Students</p>
          </div>
        </div>

        <div className="stat-card" onClick={() => navigate('/admin/faculty')}>
          <div className="stat-icon">👨‍🏫</div>
          <div className="stat-content">
            <h3 className="stat-number">{stats.faculty}</h3>
            <p className="stat-label">Faculty</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h2>⚡ Quick Actions</h2>
        <div className="actions-grid">
          <div className="action-card" onClick={() => navigate('/admin/academics')}>
            <div className="action-icon">📖</div>
            <h3>Manage Academics</h3>
            <p>Add or edit departments and courses</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/students')}>
            <div className="action-icon">👥</div>
            <h3>Manage Students</h3>
            <p>View and manage student records</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/registration-tracking')}>
            <div className="action-icon">📋</div>
            <h3>Registration Tracking</h3>
            <p>Monitor semester registration progress</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/faculty')}>
            <div className="action-icon">🎓</div>
            <h3>Manage Faculty</h3>
            <p>View and manage faculty members</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/timetables')}>
            <div className="action-icon">📅</div>
            <h3>Timetables</h3>
            <p>Upload and manage timetables</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/grades')}>
            <div className="action-icon">📊</div>
            <h3>Grades</h3>
            <p>View student grades and performance</p>
          </div>

          <div className="action-card" onClick={() => navigate('/admin/reports')}>
            <div className="action-icon">📈</div>
            <h3>Reports</h3>
            <p>Generate and view system reports</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;