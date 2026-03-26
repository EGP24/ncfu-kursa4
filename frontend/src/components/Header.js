import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/lists" className="logo">Список покупок</Link>
        <nav>
          {user ? (
            <div className="header-user">
              <span className="username">{user.username}</span>
              <button onClick={handleLogout} className="btn btn-sm">Выйти</button>
            </div>
          ) : (
            <div className="header-user">
              <Link to="/login" className="btn btn-sm">Войти</Link>
              <Link to="/register" className="btn btn-sm btn-primary">Регистрация</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
