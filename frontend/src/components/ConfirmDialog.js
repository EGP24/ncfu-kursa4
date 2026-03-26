import { useEffect } from 'react';

export default function ConfirmDialog({
  open,
  title,
  description,
  confirmText = 'Подтвердить',
  loadingText = 'Выполняем...',
  cancelText = 'Отмена',
  confirmButtonClassName = 'btn btn-danger btn-sm',
  loading = false,
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    if (!open) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && !loading) {
        onCancel();
      }
    };

    document.body.classList.add('modal-open');
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.classList.remove('modal-open');
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [open, loading, onCancel]);

  if (!open) return null;

  return (
    <div
      className="confirm-overlay"
      onClick={() => {
        if (!loading) onCancel();
      }}
    >
      <div
        className="confirm-dialog"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <h3 className="confirm-title">{title}</h3>
        {description && <p className="confirm-description">{description}</p>}

        <div className="confirm-actions">
          <button type="button" className="btn btn-sm" onClick={onCancel} disabled={loading}>
            {cancelText}
          </button>
          <button type="button" className={confirmButtonClassName} onClick={onConfirm} disabled={loading}>
            {loading ? loadingText : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
