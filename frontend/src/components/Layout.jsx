import { Outlet, useNavigate, NavLink } from 'react-router-dom';
import { tokenUtils } from '../api';
import './Layout.css';

const Layout = () => {
  const navigate = useNavigate();

  // Get user role from localStorage
  const userRole = localStorage.getItem('user_role');

  // If no role is found, try to get it from user_info
  if (!userRole) {
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      try {
        const parsed = JSON.parse(userInfo);
        if (parsed.role) {
          localStorage.setItem('user_role', parsed.role);
        }
      } catch (e) {
        console.error('Error parsing user info:', e);
      }
    }
  }

  const handleLogout = () => {
    tokenUtils.clearTokens();
    localStorage.removeItem('user_info');
    localStorage.removeItem('user_role');
    navigate('/');
  };

  // Get dashboard path based on role
  const getDashboardPath = () => {
    switch (userRole) {
      case 'ADMIN':
        return '/admin';
      case 'FACULTY':
        return '/faculty';
      case 'STUDENT':
        return '/student';
      default:
        return '/admin';
    }
  };

  // Role-based navigation items
  const getNavigationItems = () => {
    switch (userRole) {
      case 'ADMIN':
        return [
          { path: '/admin', label: 'Dashboard', icon: '', isDashboard: true },
          { path: '/admin/settings', label: 'Settings', icon: '' },
          { path: '/admin/students', label: 'Students', icon: '' },
          { path: '/admin/registration-tracking', label: 'Reg. Tracking', icon: '' },
          { path: '/admin/academics', label: 'Academics', icon: '' },
          { path: '/admin/attendance', label: 'Attendance', icon: '' },
          { path: '/admin/faculty', label: 'Faculty', icon: '' },
          { path: '/admin/grades', label: 'Grades', icon: '' },
          { path: '/admin/timetables', label: 'Timetables', icon: '' },
          { path: '/admin/exams', label: 'Exams', icon: '' },
          { path: '/admin/reports', label: 'Reports', icon: '' },
        ];
      case 'FACULTY':
        return [
          { path: '/faculty', label: 'Dashboard', icon: '', isDashboard: true },
          { path: '/faculty/attendance', label: 'Attendance', icon: '' },
          { path: '/faculty/assignments', label: 'Assignments', icon: '' },
          { path: '/faculty/exams', label: 'Exams', icon: '' },
          { path: '/faculty/reports', label: 'Reports', icon: '' },
          { path: '/faculty/timetable', label: 'My Timetable', icon: '' },
          { path: '/faculty/works', label: 'My Works', icon: '' },
        ];
      case 'STUDENT':
        return [
          { path: '/student', label: 'Dashboard', icon: '', isDashboard: true },
          { path: '/student/register', label: 'Semester Reg.', icon: '' },
          { path: '/student/timetable', label: 'Timetable', icon: '' },
          { path: '/student/attendance', label: 'My Attendance', icon: '' },
          { path: '/student/assignments', label: 'Assignments', icon: '' },
          { path: '/student/faculty', label: 'Faculty', icon: '' },
          { path: '/student/grades', label: 'Grades', icon: '' },
          { path: '/student/reports', label: 'Reports', icon: '' },
        ];
      default:
        return [
          { path: '/admin', label: '📊 Dashboard', icon: '📊', isDashboard: true },
        ];
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="layout-container">
      {/* Top Navbar */}
      <header className="layout-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="header-title">Academic ERP</h1>
            {userRole && (
              <span className="user-role-badge">
                {userRole === 'ADMIN' ? '👑 Admin' : userRole === 'FACULTY' ? '👨‍🏫 Faculty' : '👨‍🎓 Student'}
              </span>
            )}
          </div>
          <div className="header-right">
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="layout-body">
        {/* Sidebar Navigation */}
        <aside className="layout-sidebar">
          <nav className="sidebar-nav">
            <ul className="nav-list">
              {navigationItems.map((item) => (
                <li key={item.path} className="nav-item">
                  <NavLink 
                    to={item.path}
                    end={item.isDashboard}
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                  >
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="layout-main">
          <div className="main-content">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;