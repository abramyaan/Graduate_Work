import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateVacancy from './pages/CreateVacancy';
import UploadResume from './pages/UploadResume';
import Results from './pages/Results';
import CandidateDetail from './pages/CandidateDetail';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/vacancies/create"
          element={
            <ProtectedRoute>
              <CreateVacancy />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resumes/upload/:vacancyId?"
          element={
            <ProtectedRoute>
              <UploadResume />
            </ProtectedRoute>
          }
        />
        <Route
          path="/results/:vacancyId"
          element={
            <ProtectedRoute>
              <Results />
            </ProtectedRoute>
          }
        />
        <Route
          path="/candidate/:evaluationId"
          element={
            <ProtectedRoute>
              <CandidateDetail />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
