import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ListsPage from './pages/ListsPage';
import ListDetailPage from './pages/ListDetailPage';
import SharedListPage from './pages/SharedListPage';

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/lists" element={<PrivateRoute><ListsPage /></PrivateRoute>} />
      <Route path="/lists/:id" element={<PrivateRoute><ListDetailPage /></PrivateRoute>} />
      <Route path="/shared/:shareToken" element={<SharedListPage />} />
      <Route path="*" element={<Navigate to="/lists" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Header />
        <main className="container">
          <AppRoutes />
        </main>
      </BrowserRouter>
    </AuthProvider>
  );
}
