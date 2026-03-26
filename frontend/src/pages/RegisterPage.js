import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, getErrorMessage, getFieldErrors } from '../api';
import { useAuth } from '../AuthContext';
import { hasErrors, trimPayload, validateRegisterForm } from '../validation';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const payload = trimPayload({ username, password, password2 });
    const validationErrors = validateRegisterForm(payload);
    if (hasErrors(validationErrors)) {
      setFieldErrors(validationErrors);
      return;
    }

    setFieldErrors({});
    setSubmitting(true);

    try {
      const data = await api.register(payload.username, payload.password);
      login(data.token, data.user);
      navigate('/lists');
    } catch (err) {
      setFieldErrors(getFieldErrors(err));
      setError(getErrorMessage(err, 'Не удалось завершить регистрацию.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <h2>Создание аккаунта</h2>
      <form onSubmit={handleSubmit} className="auth-form">
        {error && <div className="error">{error}</div>}

        <label className="field-label" htmlFor="register-username">Имя пользователя</label>
        <input
          id="register-username"
          type="text"
          placeholder="минимум 3 символа"
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

        <label className="field-label" htmlFor="register-password">Пароль</label>
        <input
          id="register-password"
          type="password"
          placeholder="минимум 6 символов"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (fieldErrors.password) {
              setFieldErrors((prev) => ({ ...prev, password: null }));
            }
          }}
          autoComplete="new-password"
          required
        />
        {fieldErrors.password && <p className="field-error">{fieldErrors.password}</p>}

        <label className="field-label" htmlFor="register-password-repeat">Повтор пароля</label>
        <input
          id="register-password-repeat"
          type="password"
          placeholder="повторите пароль"
          value={password2}
          onChange={(e) => {
            setPassword2(e.target.value);
            if (fieldErrors.password2) {
              setFieldErrors((prev) => ({ ...prev, password2: null }));
            }
          }}
          autoComplete="new-password"
          required
        />
        {fieldErrors.password2 && <p className="field-error">{fieldErrors.password2}</p>}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Создаем аккаунт...' : 'Зарегистрироваться'}
        </button>
      </form>
      <p className="auth-link">Уже есть аккаунт? <Link to="/login">Войти</Link></p>
    </div>
  );
}
