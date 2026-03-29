import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Header from '../Header';
import { useAuth } from '../../AuthContext';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

jest.mock('../../AuthContext', () => ({
  useAuth: jest.fn(),
}));

describe('Header', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows login links for guest', () => {
    useAuth.mockReturnValue({ user: null, logout: jest.fn() });

    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Войти' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Регистрация' })).toBeInTheDocument();
  });

  it('logs out authorized user', async () => {
    const logout = jest.fn();
    useAuth.mockReturnValue({ user: { id: 1, username: 'demo' }, logout });

    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>,
    );

    await user.click(screen.getByRole('button', { name: 'Выйти' }));

    expect(logout).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
