// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

import TriageForm            from './TriageForm';
import Register              from './Register';
import Login                 from './Login';
import PatientDashboard      from './PatientDashboard';
import CareTeamDashboard     from './CareTeamDashboard';
import CareTeamPatientPage   from './CareTeamPatientPage';
import AdminDashboard        from './AdminDashboard';
import ProfilePage           from './ProfilePage';
import ViewVitals            from './ViewVitals';
import BoredChat             from './BoredChat';
import ProtectedRoute        from './ProtectedRoute';
import { useAuth }           from './AuthContext';

function App() {
  const { user, logout } = useAuth();
  const roleToDashboardPath = {
    patient:   '/dashboard',
    care_team: '/care-dashboard',
    admin:     '/admin-dashboard'
  };

  return (
    <Router>
      {/* top nav */}
      <nav className="p-4 bg-gray-100 flex justify-center space-x-4">
        {user ? (
          <>
            <Link to={roleToDashboardPath[user.role]} className="text-blue-600 underline">
              Dashboard
            </Link>
            <button
              onClick={() => {
                logout();
                window.location.href = '/login';
              }}
              className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </nav>

      {/* main routes */}
      <Routes>
        {/* public */}
        <Route path="/register" element={<Register />} />
        <Route path="/login"    element={<Login />} />

        {/* patient */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/vitals"
          element={
            <ProtectedRoute>
              <ViewVitals />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bored-chat"
          element={
            <ProtectedRoute>
              <BoredChat />
            </ProtectedRoute>
          }
        />

        {/* care team */}
        <Route
          path="/care-dashboard"
          element={
            <ProtectedRoute>
              <CareTeamDashboard />
            </ProtectedRoute>
          }
        />
        {/* ← New per-patient view for care team */}
        <Route
          path="/care-team/patient/:username"
          element={
            <ProtectedRoute>
              <CareTeamPatientPage />
            </ProtectedRoute>
          }
        />

        {/* admin */}
        <Route
          path="/admin-dashboard"
          element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;


