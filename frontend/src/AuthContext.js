import { createContext, useContext, useState, useEffect } from 'react';
import { clearAuthCookieToken, getAuthCookieToken, setAuthCookieToken, setVolatileToken } from './api';

const AuthContext = createContext(null);

function decodeTokenPayload(token) {
  if (!token) return null;

  const parts = token.split('.');
  if (parts.length < 2) return null;

  const base64Url = parts[1].replace(/-/g, '+').replace(/_/g, '/');
  const padded = `${base64Url}${'='.repeat((4 - (base64Url.length % 4)) % 4)}`;

  try {
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
}

function parseUserFromToken(token) {
  const payload = decodeTokenPayload(token);
  if (!payload || payload.user_id === undefined || payload.username === undefined) {
    return null;
  }

  return { id: payload.user_id, username: payload.username };
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getAuthCookieToken());
  const [user, setUser] = useState(() => parseUserFromToken(getAuthCookieToken()));

  useEffect(() => {
    if (token) {
      const parsedUser = parseUserFromToken(token);
      if (parsedUser) {
        setUser(parsedUser);
      } else {
        setToken(null);
        clearAuthCookieToken();
        setVolatileToken(null);
        setUser(null);
      }
    } else {
      setUser(null);
    }
  }, [token]);

  const login = (tokenValue, userData, { remember = true } = {}) => {
    if (remember) {
      setAuthCookieToken(tokenValue);
      setVolatileToken(null);
    } else {
      clearAuthCookieToken();
      setVolatileToken(tokenValue);
    }

    setToken(tokenValue);
    setUser(userData);
  };

  const logout = () => {
    clearAuthCookieToken();
    setVolatileToken(null);
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
