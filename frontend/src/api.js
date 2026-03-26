const API_BASE = '/api';
let volatileToken = null;
const AUTH_TOKEN_COOKIE_NAME = 'kursa4_auth_token';
const AUTH_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

const BACKEND_TEXT_MAP = {
  'Invalid credentials': 'Неверный логин или пароль.',
  'Authentification required': 'Нужна авторизация. Войдите и повторите.',
  'Authentication required': 'Нужна авторизация. Войдите и повторите.',
  'Username already taken': 'Это имя пользователя уже занято.',
  'List not found': 'Список не найден или доступ к нему закрыт.',
  'Item not found': 'Элемент списка не найден или уже удален.',
  'Access denied': 'У вас недостаточно прав для этого действия.',
};

const ERROR_CODE_MAP = {
  validation_error: 'Проверьте правильность заполнения полей.',
  invalid_json: 'Не удалось прочитать данные формы. Обновите страницу и попробуйте снова.',
  json_body_must_be_object: 'Некорректный формат отправленных данных.',
};

const STATUS_MESSAGE_MAP = {
  400: 'Запрос заполнен некорректно.',
  401: 'Требуется авторизация.',
  403: 'Доступ запрещен.',
  404: 'Ресурс не найден.',
  409: 'Конфликт данных. Проверьте введенную информацию.',
  500: 'Внутренняя ошибка сервера. Попробуйте позже.',
};

export class ApiError extends Error {
  constructor({ message, status, code = null, details = null, fieldErrors = {} }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.fieldErrors = fieldErrors;
  }
}

export function setVolatileToken(token) {
  volatileToken = token || null;
}

function getCookieValue(name) {
  const escapedName = name.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
  const match = document.cookie.match(new RegExp(`(?:^|; )${escapedName}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function getAuthCookieToken() {
  return getCookieValue(AUTH_TOKEN_COOKIE_NAME);
}

export function setAuthCookieToken(token) {
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';
  document.cookie = `${AUTH_TOKEN_COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; Max-Age=${AUTH_COOKIE_MAX_AGE_SECONDS}; SameSite=Lax${secure}`;
}

export function clearAuthCookieToken() {
  document.cookie = `${AUTH_TOKEN_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function getToken() {
  return volatileToken;
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function normalizeBackendText(text) {
  const trimmed = String(text || '').trim();
  if (!trimmed) return '';
  return BACKEND_TEXT_MAP[trimmed] || trimmed;
}

function extractFieldFromInstancePath(path) {
  if (!path || path === '/') return null;
  const normalized = String(path).replace(/^\//, '');
  if (!normalized) return null;
  const parts = normalized.split('/');
  const raw = parts[parts.length - 1] || '';
  return raw.replace(/~1/g, '/').replace(/~0/g, '~');
}

function humanizeValidationDetail(detail) {
  const message = String(detail?.message || '').trim();
  if (!message) return 'Некорректное значение.';

  const lower = message.toLowerCase();
  if (lower.includes('min') && lower.includes('length')) {
    return 'Значение слишком короткое.';
  }
  if (lower.includes('expected') && lower.includes('string')) {
    return 'Нужно ввести текст.';
  }
  if (lower.includes('expected') && (lower.includes('number') || lower.includes('decimal'))) {
    return 'Нужно ввести число.';
  }

  return message;
}

function parseValidationFieldErrors(details) {
  const fieldErrors = {};

  if (!Array.isArray(details)) {
    return fieldErrors;
  }

  details.forEach((detail) => {
    const field = extractFieldFromInstancePath(detail?.instance_path);
    if (!field || fieldErrors[field]) return;
    fieldErrors[field] = humanizeValidationDetail(detail);
  });

  return fieldErrors;
}

async function readResponsePayload(response) {
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function buildApiError(response, payload) {
  const status = response.status;

  if (typeof payload === 'string') {
    return new ApiError({
      message: normalizeBackendText(payload) || STATUS_MESSAGE_MAP[status] || 'Ошибка запроса.',
      status,
    });
  }

  if (payload && typeof payload === 'object') {
    const code = typeof payload.error === 'string' ? payload.error : null;
    const details = payload.details ?? null;
    const fieldErrors = code === 'validation_error' ? parseValidationFieldErrors(details) : {};
    const directMessage = typeof payload.message === 'string' ? payload.message : null;
    const codeMessage = code ? ERROR_CODE_MAP[code] : null;
    const fallback = STATUS_MESSAGE_MAP[status] || 'Ошибка запроса.';

    return new ApiError({
      message: normalizeBackendText(directMessage || codeMessage || payload.error || '') || fallback,
      status,
      code,
      details,
      fieldErrors,
    });
  }

  return new ApiError({
    message: STATUS_MESSAGE_MAP[status] || 'Ошибка запроса.',
    status,
  });
}

export function getErrorMessage(error, fallback = 'Что-то пошло не так. Попробуйте снова.') {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export function getFieldErrors(error) {
  if (error instanceof ApiError) {
    return error.fieldErrors || {};
  }
  return {};
}

async function request(method, path, body = null, extraHeaders = {}) {
  const headers = { 'Content-Type': 'application/json', ...authHeaders(), ...extraHeaders };
  const opts = { method, headers };
  if (body !== null) opts.body = JSON.stringify(body);

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, opts);
  } catch {
    throw new ApiError({
      message: 'Не удалось подключиться к серверу. Проверьте интернет или запустите backend.',
      status: 0,
    });
  }

  const payload = await readResponsePayload(res);

  if (!res.ok) {
    throw buildApiError(res, payload);
  }

  if (res.status === 204 || payload === null) {
    return null;
  }

  return payload;
}

export const api = {
  register: (username, password) => request('POST', '/auth/register', { username, password }),
  login: (username, password) => request('POST', '/auth/login', { username, password }),

  getLists: () => request('GET', '/lists'),
  createList: (title) => request('POST', '/lists', { title }),
  getList: (id) => request('GET', `/lists/${id}`),
  updateList: (id, title) => request('PUT', `/lists/${id}`, { title }),
  deleteList: (id) => request('DELETE', `/lists/${id}`),

  shareList: (id) => request('POST', `/lists/${id}/share`),
  unshareList: (id) => request('DELETE', `/lists/${id}/share`),
  getSharedList: (shareToken) => request('GET', `/shared/${shareToken}`),

  createItem: (listId, data, shareToken) => {
    const query = shareToken ? `?share_token=${shareToken}` : '';
    return request('POST', `/lists/${listId}/items${query}`, data);
  },
  updateItem: (listId, itemId, data, shareToken) => {
    const query = shareToken ? `?share_token=${shareToken}` : '';
    return request('PUT', `/lists/${listId}/items/${itemId}${query}`, data);
  },
  moveItem: (listId, itemId, position, shareToken) => {
    const query = shareToken ? `?share_token=${shareToken}` : '';
    return request('PUT', `/lists/${listId}/items/${itemId}/position${query}`, { position });
  },
  sortItems: (listId, mode, shareToken) => {
    const query = shareToken ? `?share_token=${shareToken}` : '';
    return request('PUT', `/lists/${listId}/items/sort${query}`, { mode });
  },
  deleteItem: (listId, itemId, shareToken) => {
    const query = shareToken ? `?share_token=${shareToken}` : '';
    return request('DELETE', `/lists/${listId}/items/${itemId}${query}`);
  },

  getHistory: (listId, { shareToken, actions } = {}) => {
    const params = new URLSearchParams();
    if (shareToken) {
      params.set('share_token', shareToken);
    }
    if (Array.isArray(actions)) {
      actions.forEach((action) => params.append('actions', action));
    }

    const query = params.toString();
    return request('GET', `/lists/${listId}/history${query ? `?${query}` : ''}`);
  },
};

export function connectWebSocket(listId, { token, shareToken, onMessage }) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const params = [];
  const tokenFromCookie = getAuthCookieToken();
  if (token && token !== tokenFromCookie) params.push(`token=${token}`);
  if (shareToken) params.push(`share_token=${shareToken}`);
  const query = params.length ? `?${params.join('&')}` : '';
  const url = `${protocol}//${host}/api/ws/${listId}${query}`;

  const ws = new WebSocket(url);
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onMessage(data);
    } catch {}
  };

  // Ping every 30s to keep alive
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send('ping');
    }
  }, 30000);

  ws.onclose = () => clearInterval(interval);

  return ws;
}
