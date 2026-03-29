import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ItemRow from '../ItemRow';

describe('ItemRow', () => {
  const item = {
    id: 1,
    name: 'Молоко',
    quantity: 1,
    unit: 'л',
    checked: false,
  };

  it('opens edit mode and saves updated item', async () => {
    const onUpdate = jest.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();

    render(
      <ItemRow
        item={item}
        onToggle={jest.fn()}
        onUpdate={onUpdate}
        onDelete={jest.fn()}
        unitSuggestionsId="units"
      />,
    );

    await user.click(screen.getByRole('button', { name: '✎' }));

    const textInput = screen.getByDisplayValue('Молоко');
    const qtyInput = screen.getByDisplayValue('1');
    const unitInput = screen.getByDisplayValue('л');

    await user.clear(textInput);
    await user.type(textInput, 'Сыр');
    await user.clear(qtyInput);
    await user.type(qtyInput, '2');
    await user.clear(unitInput);
    await user.type(unitInput, 'кг');

    await user.click(screen.getByRole('button', { name: '✓' }));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith({ name: 'Сыр', quantity: 2, unit: 'кг' });
    });
  });

  it('shows validation error and does not call update for invalid data', async () => {
    const onUpdate = jest.fn();
    const user = userEvent.setup();

    render(
      <ItemRow
        item={item}
        onToggle={jest.fn()}
        onUpdate={onUpdate}
        onDelete={jest.fn()}
        unitSuggestionsId="units"
      />,
    );

    await user.click(screen.getByRole('button', { name: '✎' }));

    const qtyInput = screen.getByDisplayValue('1');
    await user.clear(qtyInput);
    await user.type(qtyInput, '0');
    await user.click(screen.getByRole('button', { name: '✓' }));

    expect(screen.getByText('Количество должно быть больше 0.')).toBeInTheDocument();
    expect(onUpdate).not.toHaveBeenCalled();
  });
});
