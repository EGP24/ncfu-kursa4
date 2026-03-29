import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { api } from '../../api';

const mockLogin = jest.fn();

jest.mock('../../AuthContext', () => ({
  useAuth: () => ({ login: mockLogin }),
}));

jest.mock('../../api', () => ({
  api: {
    login: jest.fn(),
  },
  getErrorMessage: jest.fn((error, fallback) => fallback),
  getFieldErrors: jest.fn(() => ({})),
}));

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('logs in user and redirects to lists', async () => {
    api.login.mockResolvedValue({
      token: 'header.payload.signature',
      user: { id: 1, username: 'demo' },
    });

    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/lists" element={<div>Списки</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText('Имя пользователя'), 'demo');
    await user.type(screen.getByLabelText('Пароль'), 'secret123');
    await user.click(screen.getByLabelText('Запомнить меня'));
    await user.click(screen.getByRole('button', { name: 'Войти' }));

    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith('demo', 'secret123');
      expect(mockLogin).toHaveBeenCalledWith(
        'header.payload.signature',
        { id: 1, username: 'demo' },
        { remember: true },
      );
    });

    expect(screen.getByText('Списки')).toBeInTheDocument();
  });
});
