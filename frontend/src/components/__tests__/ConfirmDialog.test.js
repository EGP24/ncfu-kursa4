import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConfirmDialog from '../ConfirmDialog';

describe('ConfirmDialog', () => {
  it('renders and handles confirm/cancel actions', async () => {
    const onConfirm = jest.fn();
    const onCancel = jest.fn();
    const user = userEvent.setup();

    render(
      <ConfirmDialog
        open
        title="Удалить?"
        description="Подтвердите"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />,
    );

    expect(screen.getByRole('dialog', { name: 'Удалить?' })).toBeInTheDocument();
    expect(document.body.classList.contains('modal-open')).toBe(true);

    await user.click(screen.getByRole('button', { name: 'Подтвердить' }));
    await user.click(screen.getByRole('button', { name: 'Отмена' }));

    expect(onConfirm).toHaveBeenCalledTimes(1);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('closes on Escape when not loading', () => {
    const onCancel = jest.fn();

    render(
      <ConfirmDialog
        open
        title="Удалить?"
        onConfirm={jest.fn()}
        onCancel={onCancel}
      />,
    );

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
