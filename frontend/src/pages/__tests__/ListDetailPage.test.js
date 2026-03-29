import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ListDetailPage from '../ListDetailPage';
import { api } from '../../api';

jest.mock('../../AuthContext', () => ({
  useAuth: () => ({ token: 'test-token' }),
}));

jest.mock('../../api', () => ({
  api: {
    getList: jest.fn(),
    createItem: jest.fn(),
    updateItem: jest.fn(),
    deleteItem: jest.fn(),
    sortItems: jest.fn(),
    moveItem: jest.fn(),
    shareList: jest.fn(),
    unshareList: jest.fn(),
    updateList: jest.fn(),
  },
  connectWebSocket: jest.fn(() => ({ close: jest.fn() })),
  getErrorMessage: jest.fn((error, fallback) => fallback),
  getFieldErrors: jest.fn(() => ({})),
}));

jest.mock('../../components/ItemRow', () => () => <li data-testid="item-row" />);
jest.mock('../../components/ConfirmDialog', () => () => null);
jest.mock('../../components/HistoryPanel', () => () => <div>История</div>);

describe('ListDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('adds new item from the form', async () => {
    api.getList.mockResolvedValue({
      id: 1,
      title: 'Семейные покупки',
      share_token: null,
      items: [],
    });
    api.createItem.mockResolvedValue({ id: 42 });

    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/lists/1']}>
        <Routes>
          <Route path="/lists/:id" element={<ListDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByText('Семейные покупки');

    await user.type(screen.getByPlaceholderText('Название товара...'), 'Молоко');

    const qtyInput = screen.getByRole('spinbutton');
    await user.clear(qtyInput);
    await user.type(qtyInput, '2');

    await user.type(screen.getByPlaceholderText('ед.'), 'л');
    await user.click(screen.getByRole('button', { name: 'Добавить' }));

    await waitFor(() => {
      expect(api.createItem).toHaveBeenCalledWith('1', {
        name: 'Молоко',
        quantity: 2,
        unit: 'л',
      });
    });

    expect(screen.getByPlaceholderText('Название товара...')).toHaveValue('');
    expect(screen.getByRole('spinbutton')).toHaveValue(1);
    expect(screen.getByPlaceholderText('ед.')).toHaveValue('');
  });
});
