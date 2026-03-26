import { useEffect, useState } from 'react';
import { getErrorMessage } from '../api';
import { hasErrors, trimPayload, validateItemPayload } from '../validation';

export default function ItemRow({
  item,
  onToggle,
  onUpdate,
  onDelete,
  unitSuggestionsId,
  dragEnabled = false,
  isDragging = false,
  onDragStart,
  onDragOver,
  onDragEnd,
}) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(item.name);
  const [quantity, setQuantity] = useState(item.quantity);
  const [unit, setUnit] = useState(item.unit);
  const [rowError, setRowError] = useState('');
  const [saving, setSaving] = useState(false);

  const canDrag = dragEnabled && !editing && !saving;

  useEffect(() => {
    if (editing) return;
    setName(item.name);
    setQuantity(item.quantity);
    setUnit(item.unit || '');
  }, [item, editing]);

  const handleSave = async () => {
    const payload = trimPayload({ name, quantity, unit });
    const validationErrors = validateItemPayload(payload);
    if (hasErrors(validationErrors)) {
      setRowError(validationErrors.name || validationErrors.quantity || validationErrors.unit);
      return;
    }

    setRowError('');
    setSaving(true);

    try {
      await onUpdate({
        name: payload.name,
        quantity: Number(payload.quantity),
        unit: payload.unit || null,
      });
      setEditing(false);
    } catch (err) {
      setRowError(getErrorMessage(err, 'Не удалось сохранить изменения.'));
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setName(item.name);
    setQuantity(item.quantity);
    setUnit(item.unit || '');
    setRowError('');
    setEditing(false);
  };

  if (editing) {
    return (
      <li className="item-row editing">
        <div className="item-edit-grid">
          <input
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              if (rowError) setRowError('');
            }}
            className="item-name-input"
          />
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={quantity}
            onChange={(e) => {
              setQuantity(e.target.value);
              if (rowError) setRowError('');
            }}
            className="item-qty-input"
          />
          <input
            type="text"
            value={unit}
            list={unitSuggestionsId}
            onChange={(e) => {
              setUnit(e.target.value);
              if (rowError) setRowError('');
            }}
            className="item-unit-input"
            placeholder="ед."
          />
          <button className="btn btn-sm btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '...' : '✓'}
          </button>
          <button className="btn btn-sm" onClick={handleCancel} disabled={saving}>✕</button>
        </div>
        {rowError && <p className="field-error inline-field-error">{rowError}</p>}
      </li>
    );
  }

  return (
    <li
      className={`item-row ${item.checked ? 'checked' : ''} ${isDragging ? 'dragging' : ''}`}
      draggable={canDrag}
      onDragStart={(event) => onDragStart?.(event, item.id)}
      onDragOver={(event) => onDragOver?.(event, item.id)}
      onDragEnd={onDragEnd}
      onDrop={(event) => event.preventDefault()}
    >
      <span className="drag-grip" title="Зажмите и перетащите">::</span>
      <label className="item-check">
        <input type="checkbox" checked={item.checked} onChange={onToggle} />
        <span className="checkmark"></span>
      </label>
      <span className="item-info" onDoubleClick={() => setEditing(true)} title="Двойной клик для редактирования">
        <span className="item-name">{item.name}</span>
        <span className="item-qty">{item.quantity}{item.unit ? ` ${item.unit}` : ''}</span>
      </span>
      <div className="item-actions">
        <button className="btn btn-sm" onClick={() => setEditing(true)}>✎</button>
        <button className="btn btn-sm btn-danger" onClick={onDelete}>✕</button>
      </div>
    </li>
  );
}
