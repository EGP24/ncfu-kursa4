import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SharedListPage from '../SharedListPage';
import { api } from '../../api';

jest.mock('../../api', () => ({
  api: {
    getSharedList: jest.fn(),
    createItem: jest.fn(),
    updateItem: jest.fn(),
    deleteItem: jest.fn(),
    sortItems: jest.fn(),
    moveItem: jest.fn(),
  },
  connectWebSocket: jest.fn(() => ({ close: jest.fn() })),
  getErrorMessage: jest.fn((error, fallback) => fallback),
  getFieldErrors: jest.fn(() => ({})),
}));

jest.mock('../../components/ItemRow', () => () => <li data-testid="item-row" />);
jest.mock('../../components/ConfirmDialog', () => () => null);
jest.mock('../../components/HistoryPanel', () => () => <div>История</div>);

describe('SharedListPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads shared list and creates item with share token', async () => {
    api.getSharedList.mockResolvedValue({
      id: 21,
      title: 'Общий список',
      items: [],
    });
    api.createItem.mockResolvedValue({ id: 9 });

    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/shared/token-123']}>
        <Routes>
          <Route path="/shared/:shareToken" element={<SharedListPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await screen.findByRole('heading', { name: 'Общий список' });

    await user.type(screen.getByPlaceholderText('Название товара...'), 'Яблоки');
    await user.clear(screen.getByRole('spinbutton'));
    await user.type(screen.getByRole('spinbutton'), '3');
    await user.type(screen.getByPlaceholderText('ед.'), 'кг');
    await user.click(screen.getByRole('button', { name: 'Добавить' }));

    await waitFor(() => {
      expect(api.createItem).toHaveBeenCalledWith(
        21,
        { name: 'Яблоки', quantity: 3, unit: 'кг' },
        'token-123',
      );
    });
  });
});
