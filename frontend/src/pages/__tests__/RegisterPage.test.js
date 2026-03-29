import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import RegisterPage from '../RegisterPage';
import { api } from '../../api';

const mockLogin = jest.fn();

jest.mock('../../AuthContext', () => ({
  useAuth: () => ({ login: mockLogin }),
}));

jest.mock('../../api', () => ({
  api: {
    register: jest.fn(),
  },
  getErrorMessage: jest.fn((error, fallback) => fallback),
  getFieldErrors: jest.fn(() => ({})),
}));

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('registers user and redirects to lists', async () => {
    api.register.mockResolvedValue({
      token: 'header.payload.signature',
      user: { id: 7, username: 'new-user' },
    });

    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/register']}>
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/lists" element={<div>Списки</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText('Имя пользователя'), 'new-user');
    await user.type(screen.getByLabelText('Пароль'), 'secret123');
    await user.type(screen.getByLabelText('Повтор пароля'), 'secret123');
    await user.click(screen.getByRole('button', { name: 'Зарегистрироваться' }));

    await waitFor(() => {
      expect(api.register).toHaveBeenCalledWith('new-user', 'secret123');
      expect(mockLogin).toHaveBeenCalledWith('header.payload.signature', { id: 7, username: 'new-user' });
    });

    expect(screen.getByText('Списки')).toBeInTheDocument();
  });
});
