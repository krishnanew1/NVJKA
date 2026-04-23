import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { authAPI, tokenUtils } from '../api';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await authAPI.login(formData);
      const { access, refresh, user } = response.data;

      // Save tokens to localStorage
      tokenUtils.setTokens(access, refresh);

      // Get user info from JWT token if not provided in response
      let userInfo = user;
      if (!userInfo && access) {
        try {
          const decoded = jwtDecode(access);
          userInfo = {
            id: decoded.user_id,
            role: decoded.role,
            first_name: decoded.first_name,
            last_name: decoded.last_name,
            email: decoded.email,
          };
        } catch (decodeError) {
          console.warn('Could not decode JWT token:', decodeError);
        }
      }

      // Save user info if available
      if (userInfo) {
        localStorage.setItem('user_info', JSON.stringify(userInfo));
        // Store user role separately for easy access
        localStorage.setItem('user_role', userInfo.role);
      }

      setSuccess('Login successful! Redirecting...');
      
      // Redirect based on user role
      setTimeout(() => {
        if (userInfo && userInfo.role) {
          switch (userInfo.role) {
            case 'ADMIN':
              navigate('/admin');
              break;
            case 'FACULTY':
              navigate('/faculty');
              break;
            case 'STUDENT':
              navigate('/student');
              break;
            default:
              navigate('/student'); // Default fallback
          }
        } else {
          // Fallback if no role info available
          navigate('/student');
        }
      }, 500);

    } catch (err) {
      console.error('Login error:', err);
      
      if (err.response?.status === 401) {
        setError('Invalid username or password. Please try again.');
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message === 'Network Error') {
        setError('Unable to connect to server. Please check if the backend is running.');
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Academic ERP</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Enter your username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              {success}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="login-footer">
          <p>Demo Credentials:</p>
          <div className="demo-credentials">
            <small>Admin: admin_demo / Admin@2026</small>
            <small>Faculty: prof_smith / Faculty@2026</small>
            <small>Student: john_doe / Student@2026</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;