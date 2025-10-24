import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { AdminPage } from './pages/AdminPage';
import TestAdminPage from './pages/TestAdminPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <div className="arena-container min-h-screen">
                <Header />
                <main>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/knowledge" element={<KnowledgeBasePage />} />
                    <Route path="/admin" element={<AdminPage />} />
                    <Route path="/test-admin" element={<TestAdminPage />} />
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
