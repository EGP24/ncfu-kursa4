import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import ListsPage from '../ListsPage';
import { api } from '../../api';

jest.mock('../../api', () => ({
  api: {
    getLists: jest.fn(),
    createList: jest.fn(),
    deleteList: jest.fn(),
  },
  getErrorMessage: jest.fn((error, fallback) => fallback),
  getFieldErrors: jest.fn(() => ({})),
}));

jest.mock('../../components/ConfirmDialog', () => ({
  open,
  onConfirm,
  onCancel,
}) => (
  open ? (
    <div>
      <button onClick={onConfirm}>Подтвердить удаление</button>
      <button onClick={onCancel}>Отмена удаления</button>
    </div>
  ) : null
));

describe('ListsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads lists and creates a new list', async () => {
    api.getLists
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        { id: 1, title: 'Покупки', created_at: '2026-03-01T10:00:00.000Z' },
      ]);
    api.createList.mockResolvedValue({ id: 1 });

    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <ListsPage />
      </MemoryRouter>,
    );

    await screen.findByText('Списков пока нет. Создайте первый!');

    await user.type(screen.getByPlaceholderText('Например: Продукты на неделю'), '  Покупки  ');
    await user.click(screen.getByRole('button', { name: 'Создать' }));

    await waitFor(() => {
      expect(api.createList).toHaveBeenCalledWith('Покупки');
      expect(api.getLists).toHaveBeenCalledTimes(2);
    });

    expect(screen.getByText('Покупки')).toBeInTheDocument();
  });

  it('deletes list after confirmation', async () => {
    api.getLists.mockResolvedValue([
      { id: 3, title: 'Удаляемый список', created_at: '2026-03-01T10:00:00.000Z' },
    ]);
    api.deleteList.mockResolvedValue(null);

    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <ListsPage />
      </MemoryRouter>,
    );

    await screen.findByText('Удаляемый список');
    await user.click(screen.getByRole('button', { name: '✕' }));
    await user.click(screen.getByRole('button', { name: 'Подтвердить удаление' }));

    await waitFor(() => {
      expect(api.deleteList).toHaveBeenCalledWith(3);
    });
  });
});
