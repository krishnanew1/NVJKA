import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import AdminDashboard from './pages/AdminDashboard';
import AdminSettings from './pages/AdminSettings';
import AdminStudents from './pages/AdminStudents';
import AdminRegTracking from './pages/AdminRegTracking';
import AdminFaculty from './pages/AdminFaculty';
import AdminGrades from './pages/AdminGrades';
import FacultyDashboard from './pages/FacultyDashboard';
import FacultyAttendance from './pages/FacultyAttendance';
import FacultyExams from './pages/FacultyExams';
import StudentDashboard from './pages/StudentDashboard';
import StudentTimetable from './pages/StudentTimetable';
import StudentGrades from './pages/StudentGrades';
import StudentRegistration from './pages/StudentRegistration';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Login />} />
          
          {/* Legacy Dashboard Route (for backward compatibility) */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Protected Routes with Layout */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<AdminDashboard />} />
            <Route path="settings" element={<AdminSettings />} />
            <Route path="students" element={<AdminStudents />} />
            <Route path="registration-tracking" element={<AdminRegTracking />} />
            <Route path="faculty" element={<AdminFaculty />} />
            <Route path="grades" element={<AdminGrades />} />
          </Route>
          
          <Route 
            path="/faculty" 
            element={
              <ProtectedRoute allowedRoles={['FACULTY']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<FacultyDashboard />} />
            <Route path="attendance" element={<FacultyAttendance />} />
            <Route path="exams" element={<FacultyExams />} />
          </Route>
          
          <Route 
            path="/student" 
            element={
              <ProtectedRoute allowedRoles={['STUDENT']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<StudentDashboard />} />
            <Route path="register" element={<StudentRegistration />} />
            <Route path="timetable" element={<StudentTimetable />} />
            <Route path="grades" element={<StudentGrades />} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;