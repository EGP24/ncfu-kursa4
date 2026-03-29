import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import HistoryPanel from '../HistoryPanel';
import { api } from '../../api';

jest.mock('../../api', () => ({
  api: {
    getHistory: jest.fn(),
  },
  getErrorMessage: jest.fn((error, fallback) => fallback),
}));

describe('HistoryPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads and renders history records after opening panel', async () => {
    api.getHistory.mockResolvedValue([
      {
        id: 1,
        action: 'item_added',
        item_name: 'Кофе',
        details: 'Количество: 1',
        username: 'demo',
        created_at: '2026-03-01T10:00:00.000Z',
      },
    ]);

    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/lists/1']}>
        <Routes>
          <Route path="/lists/:id" element={<HistoryPanel listId={1} historyKey={0} />} />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(screen.getByRole('button', { name: 'История изменений' }));

    await waitFor(() => {
      expect(api.getHistory).toHaveBeenCalledWith(1, {
        shareToken: undefined,
        actions: undefined,
      });
    });

    expect(screen.getByText('Кофе')).toBeInTheDocument();
    expect(screen.getByText('demo')).toBeInTheDocument();
  });
});
