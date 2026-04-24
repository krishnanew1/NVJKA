import { Outlet, useNavigate, NavLink } from 'react-router-dom';
import { tokenUtils } from '../api';
import './Layout.css';

const RoleBasedLayout = ({ role = 'admin' }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    tokenUtils.clearTokens();
    navigate('/');
  };

  // Navigation items based on role
  const getNavigationItems = () => {
    const baseItems = [
      { path: `/${role}`, label: '📊 Dashboard', icon: '📊', isDashboard: true }
    ];

    switch (role) {
      case 'admin':
        return [
          ...baseItems,
          { path: '/admin/academics', label: '🏫 Academics', icon: '🏫' },
          { path: '/admin/faculty', label: '👨‍🏫 Faculty', icon: '👨‍🏫' },
          { path: '/admin/students', label: '👨‍🎓 Students', icon: '👨‍🎓' },
          { path: '/admin/timetables', label: '📅 Timetables', icon: '📅' },
          { path: '/admin/attendance', label: '📋 Attendance', icon: '📋' },
        ];
      
      case 'faculty':
        return [
          ...baseItems,
          { path: '/faculty/assignments', label: '📚 My Classes', icon: '📚' },
          { path: '/faculty/grades', label: '📝 Enter Grades', icon: '📝' },
          { path: '/faculty/timetable', label: '📅 My Timetable', icon: '📅' },
          { path: '/faculty/students', label: '👨‍🎓 My Students', icon: '👨‍🎓' },
        ];
      
      case 'student':
        return [
          ...baseItems,
          { path: '/student/courses', label: '📚 My Courses', icon: '📚' },
          { path: '/student/timetable', label: '📅 My Timetable', icon: '📅' },
          { path: '/student/transcript', label: '📊 My Transcript', icon: '📊' },
          { path: '/student/attendance', label: '📋 My Attendance', icon: '📋' },
        ];
      
      default:
        return baseItems;
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
            <span className="role-badge">{role.charAt(0).toUpperCase() + role.slice(1)}</span>
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

export default RoleBasedLayout;