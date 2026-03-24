import axios from 'axios';

// Global toast notification function (will be set by App.jsx)
let globalShowToast = null;

export const setGlobalToast = (toastFunction) => {
  globalShowToast = toastFunction;
};

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically attach access token
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and auto-logout
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // If we get a 401 and haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('http://127.0.0.1:8000/api/auth/token/refresh/', {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed - session expired, auto-logout
          tokenUtils.clearTokens();
          
          // Show toast notification if available
          if (globalShowToast) {
            globalShowToast('Session expired. Please log in again.', 'error');
          }
          
          // Redirect to login after a short delay
          setTimeout(() => {
            window.location.href = '/';
          }, 1500);
          
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available - auto-logout
        tokenUtils.clearTokens();
        
        // Show toast notification if available
        if (globalShowToast) {
          globalShowToast('Session expired. Please log in again.', 'error');
        }
        
        // Redirect to login after a short delay
        setTimeout(() => {
          window.location.href = '/';
        }, 1500);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API functions
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login/', credentials),
  refreshToken: (refreshToken) => api.post('/api/auth/token/refresh/', { refresh: refreshToken }),
};

// Academic API functions (for future use)
export const academicAPI = {
  getDepartments: () => api.get('/api/academics/departments/'),
  getCourses: () => api.get('/api/academics/courses/'),
  getSubjects: () => api.get('/api/academics/subjects/'),
  generateTimetable: (data) => api.post('/api/academics/timetable/generate/', data),
  getBatchTimetable: (params) => api.get('/api/academics/timetable/batch/', { params }),
};

// Student API functions (for future use)
export const studentAPI = {
  getEnrollments: () => api.get('/api/students/enrollments/'),
  getTranscript: (studentId) => api.get(`/api/exams/transcript/${studentId}/`),
};

// Attendance API functions (for future use)
export const attendanceAPI = {
  markBulkAttendance: (data) => api.post('/api/attendance/bulk-mark/', data),
};

// Utility functions
export const tokenUtils = {
  getAccessToken: () => localStorage.getItem('access_token'),
  getRefreshToken: () => localStorage.getItem('refresh_token'),
  getUserInfo: () => {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  },
  getUserRole: () => {
    return localStorage.getItem('user_role');
  },
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  },
  clearTokens: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('user_role');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export default api;