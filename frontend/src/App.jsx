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
import AdminTimetables from './pages/AdminTimetables';
import AdminAcademics from './pages/AdminAcademics';
import AdminAttendance from './pages/AdminAttendance';
import FacultyDashboard from './pages/FacultyDashboard';
import FacultyGrades from './pages/FacultyGrades';
import FacultyAttendance from './pages/FacultyAttendance';
import FacultyTimetable from './pages/FacultyTimetable';
import FacultyWorks from './pages/FacultyWorks';
import StudentDashboard from './pages/StudentDashboard';
import StudentTimetable from './pages/StudentTimetable';
import StudentGrades from './pages/StudentGrades';
import StudentRegistration from './pages/StudentRegistration';
import StudentAttendance from './pages/StudentAttendance';
import StudentReports from './pages/StudentReports';
import StudentFaculty from './pages/StudentFaculty';
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
            <Route path="academics" element={<AdminAcademics />} />
            <Route path="attendance" element={<AdminAttendance />} />
            <Route path="grades" element={<AdminGrades />} />
            <Route path="timetables" element={<AdminTimetables />} />
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
            <Route path="grades" element={<FacultyGrades />} />
            <Route path="attendance" element={<FacultyAttendance />} />
            <Route path="timetable" element={<FacultyTimetable />} />
            <Route path="works" element={<FacultyWorks />} />
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
            <Route path="attendance" element={<StudentAttendance />} />
            <Route path="faculty" element={<StudentFaculty />} />
            <Route path="grades" element={<StudentGrades />} />
            <Route path="reports" element={<StudentReports />} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;