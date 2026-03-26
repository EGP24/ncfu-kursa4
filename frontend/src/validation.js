function normalizeText(value) {
  return String(value || '').trim();
}

function asNumber(value) {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}

export function validateLoginForm({ username, password }) {
  const errors = {};

  if (!normalizeText(username)) {
    errors.username = 'Введите имя пользователя.';
  }
  if (!password) {
    errors.password = 'Введите пароль.';
  }

  return errors;
}

export function validateRegisterForm({ username, password, password2 }) {
  const errors = {};
  const trimmedUsername = normalizeText(username);

  if (!trimmedUsername) {
    errors.username = 'Введите имя пользователя.';
  } else if (trimmedUsername.length < 3) {
    errors.username = 'Имя пользователя должно быть не короче 3 символов.';
  } else if (trimmedUsername.length > 32) {
    errors.username = 'Имя пользователя должно быть не длиннее 32 символов.';
  }

  if (!password) {
    errors.password = 'Введите пароль.';
  } else if (password.length < 6) {
    errors.password = 'Пароль должен быть не короче 6 символов.';
  }

  if (!password2) {
    errors.password2 = 'Повторите пароль.';
  } else if (password !== password2) {
    errors.password2 = 'Пароли не совпадают.';
  }

  return errors;
}

export function validateListTitle(title) {
  const errors = {};
  const value = normalizeText(title);

  if (!value) {
    errors.title = 'Введите название списка.';
  } else if (value.length > 80) {
    errors.title = 'Название списка должно быть не длиннее 80 символов.';
  }

  return errors;
}

export function validateItemPayload({ name, quantity, unit }) {
  const errors = {};
  const normalizedName = normalizeText(name);
  const normalizedUnit = normalizeText(unit);
  const quantityNumber = asNumber(quantity);

  if (!normalizedName) {
    errors.name = 'Введите название товара.';
  } else if (normalizedName.length > 100) {
    errors.name = 'Название товара должно быть не длиннее 100 символов.';
  }

  if (quantityNumber === null || quantityNumber <= 0) {
    errors.quantity = 'Количество должно быть больше 0.';
  }

  if (normalizedUnit.length > 15) {
    errors.unit = 'Единица измерения должна быть не длиннее 15 символов.';
  }

  return errors;
}

export function trimPayload(payload) {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => {
      if (typeof value === 'string') {
        return [key, value.trim()];
      }
      return [key, value];
    }),
  );
}
