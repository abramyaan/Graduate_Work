import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './context/ToastContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateVacancy from './pages/CreateVacancy';
import EditVacancy from './pages/EditVacancy';
import UploadResume from './pages/UploadResume';
import Results from './pages/Results';
import CandidateDetail from './pages/CandidateDetail';
import Candidates from './pages/Candidates';
import EditCandidate from './pages/EditCandidate';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => {
  return (
    <ToastProvider>
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
            path="/vacancies/edit/:vacancyId"
            element={
              <ProtectedRoute>
                <EditVacancy />
              </ProtectedRoute>
            }
          />
          <Route
            path="/candidates"
            element={
              <ProtectedRoute>
                <Candidates />
              </ProtectedRoute>
            }
          />
          <Route
            path="/candidates/edit/:candidateId"
            element={
              <ProtectedRoute>
                <EditCandidate />
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
    </ToastProvider>
  );
};

export default App;
