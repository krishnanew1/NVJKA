import { Navigate, useLocation } from 'react-router-dom';
import { tokenUtils } from '../api';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const isAuthenticated = tokenUtils.isAuthenticated();
  const userRole = tokenUtils.getUserRole();
  const location = useLocation();
  
  if (!isAuthenticated) {
    // Redirect to login page if not authenticated
    return <Navigate to="/" replace />;
  }

  // If allowedRoles is specified, check if user has permission
  if (allowedRoles && allowedRoles.length > 0) {
    if (!userRole || !allowedRoles.includes(userRole)) {
      // Redirect to appropriate dashboard based on role
      const redirectPath = getRoleDashboard(userRole);
      return <Navigate to={redirectPath} replace />;
    }
  }
  
  // Render children if authenticated and authorized
  return children;
};

// Helper function to get dashboard path based on role
const getRoleDashboard = (role) => {
  switch (role) {
    case 'ADMIN':
      return '/admin';
    case 'FACULTY':
      return '/faculty';
    case 'STUDENT':
      return '/student';
    default:
      return '/';
  }
};

export default ProtectedRoute;