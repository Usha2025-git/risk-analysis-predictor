import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import { useAuthStore } from './store/authStore';
import LoadingSpinner from './components/common/LoadingSpinner';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import RiskAnalysis from './pages/RiskAnalysis';
import ResourceManagement from './pages/ResourceManagement';
import Analytics from './pages/Analytics';
import Layout from './components/layout/Layout';

function AuthGate({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const hydrate = useAuthStore((s) => s.hydrate);
  const loginDemo = useAuthStore((s) => s.loginDemo);
  const attemptedRef = useRef(false);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (attemptedRef.current) return;
    if (isAuthenticated) return;
    if (isLoading) return;

    attemptedRef.current = true;
    void loginDemo();
  }, [isAuthenticated, isLoading, loginDemo]);

  if (!isAuthenticated) {
    return <LoadingSpinner />;
  }

  return <Layout>{children}</Layout>;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route 
          path="/dashboard" 
          element={<AuthGate><Dashboard /></AuthGate>}
        />
        <Route 
          path="/projects" 
          element={<AuthGate><Projects /></AuthGate>}
        />
        <Route 
          path="/projects/:id" 
          element={<AuthGate><ProjectDetail /></AuthGate>}
        />
        <Route 
          path="/risks" 
          element={<AuthGate><RiskAnalysis /></AuthGate>}
        />
        <Route 
          path="/resources" 
          element={<AuthGate><ResourceManagement /></AuthGate>}
        />
        <Route 
          path="/analytics" 
          element={<AuthGate><Analytics /></AuthGate>}
        />
        <Route 
          path="/" 
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </Router>
  );
}

export default App;
