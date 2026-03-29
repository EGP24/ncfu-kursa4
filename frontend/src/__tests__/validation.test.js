import {
  hasErrors,
  trimPayload,
  validateItemPayload,
  validateListTitle,
  validateLoginForm,
  validateRegisterForm,
} from '../validation';

describe('validation helpers', () => {
  it('validates login form', () => {
    expect(validateLoginForm({ username: '', password: '' })).toEqual({
      username: 'Введите имя пользователя.',
      password: 'Введите пароль.',
    });

    expect(validateLoginForm({ username: 'demo', password: 'secret' })).toEqual({});
  });

  it('validates register form', () => {
    expect(validateRegisterForm({ username: 'ab', password: '123', password2: '12' })).toEqual({
      username: 'Имя пользователя должно быть не короче 3 символов.',
      password: 'Пароль должен быть не короче 6 символов.',
      password2: 'Пароли не совпадают.',
    });
  });

  it('validates list title and item payload', () => {
    expect(validateListTitle('   ')).toEqual({ title: 'Введите название списка.' });
    expect(validateListTitle('Покупки')).toEqual({});

    expect(validateItemPayload({ name: '', quantity: 0, unit: 'x'.repeat(20) })).toEqual({
      name: 'Введите название товара.',
      quantity: 'Количество должно быть больше 0.',
      unit: 'Единица измерения должна быть не длиннее 15 символов.',
    });
  });

  it('trims payload and detects errors object', () => {
    expect(trimPayload({ name: '  milk  ', quantity: 2 })).toEqual({ name: 'milk', quantity: 2 });
    expect(hasErrors({})).toBe(false);
    expect(hasErrors({ name: 'err' })).toBe(true);
  });
});
