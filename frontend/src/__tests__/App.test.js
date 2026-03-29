import { render, screen } from '@testing-library/react';
import App from '../App';
import { useAuth } from '../AuthContext';

jest.mock('../components/Header', () => () => <div>Header</div>);
jest.mock('../pages/LoginPage', () => () => <div>Login Page</div>);
jest.mock('../pages/RegisterPage', () => () => <div>Register Page</div>);
jest.mock('../pages/ListsPage', () => () => <div>Lists Page</div>);
jest.mock('../pages/ListDetailPage', () => () => <div>List Detail Page</div>);
jest.mock('../pages/SharedListPage', () => () => <div>Shared List Page</div>);

jest.mock('../AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: jest.fn(),
}));

describe('App routing', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/');
    jest.clearAllMocks();
  });

  it('redirects guest from private route to login', () => {
    useAuth.mockReturnValue({ user: null });
    window.history.pushState({}, '', '/lists');

    render(<App />);

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('renders private page for authorized user', () => {
    useAuth.mockReturnValue({ user: { id: 1, username: 'demo' } });
    window.history.pushState({}, '', '/lists');

    render(<App />);

    expect(screen.getByText('Lists Page')).toBeInTheDocument();
  });
});
