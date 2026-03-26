import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, getErrorMessage, getFieldErrors } from '../api';
import { useAuth } from '../AuthContext';
import { hasErrors, trimPayload, validateLoginForm } from '../validation';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const payload = trimPayload({ username, password });
    const validationErrors = validateLoginForm(payload);
    if (hasErrors(validationErrors)) {
      setFieldErrors(validationErrors);
      return;
    }

    setFieldErrors({});
    setSubmitting(true);

    try {
      const data = await api.login(payload.username, payload.password);
      login(data.token, data.user, { remember: rememberMe });
      navigate('/lists');
    } catch (err) {
      setFieldErrors(getFieldErrors(err));
      setError(getErrorMessage(err, 'Не удалось войти. Проверьте данные и попробуйте снова.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <h2>Вход в аккаунт</h2>
      <form onSubmit={handleSubmit} className="auth-form">
        {error && <div className="error">{error}</div>}

        <label className="field-label" htmlFor="login-username">Имя пользователя</label>
        <input
          id="login-username"
          type="text"
          placeholder="Введите имя"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            if (fieldErrors.username) {
              setFieldErrors((prev) => ({ ...prev, username: null }));
            }
          }}
          autoComplete="username"
          required
        />
        {fieldErrors.username && <p className="field-error">{fieldErrors.username}</p>}

        <label className="field-label" htmlFor="login-password">Пароль</label>
        <input
          id="login-password"
          type="password"
          placeholder="Введите пароль"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (fieldErrors.password) {
              setFieldErrors((prev) => ({ ...prev, password: null }));
            }
          }}
          autoComplete="current-password"
          required
        />
        {fieldErrors.password && <p className="field-error">{fieldErrors.password}</p>}

        <label className="remember-row" htmlFor="login-remember">
          <input
            id="login-remember"
            type="checkbox"
            checked={rememberMe}
            onChange={(event) => setRememberMe(event.target.checked)}
          />
          <span>Запомнить меня</span>
        </label>

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Входим...' : 'Войти'}
        </button>
      </form>
      <p className="auth-link">Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
    </div>
  );
}
