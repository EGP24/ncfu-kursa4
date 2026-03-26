import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, getErrorMessage, getFieldErrors } from '../api';
import ConfirmDialog from '../components/ConfirmDialog';
import { hasErrors, trimPayload, validateListTitle } from '../validation';

export default function ListsPage() {
  const [lists, setLists] = useState([]);
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [confirmDeleteListId, setConfirmDeleteListId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadLists = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getLists();
      setLists(data);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось загрузить списки.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLists();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();

    const payload = trimPayload({ title });
    const validationErrors = validateListTitle(payload.title);
    if (hasErrors(validationErrors)) {
      setFieldErrors(validationErrors);
      return;
    }

    setFieldErrors({});
    setSubmitting(true);

    try {
      await api.createList(payload.title);
      setTitle('');
      await loadLists();
    } catch (err) {
      const backendFieldErrors = getFieldErrors(err);
      if (hasErrors(backendFieldErrors)) {
        setFieldErrors((prev) => ({ ...prev, ...backendFieldErrors }));
      }
      setError(getErrorMessage(err, 'Не удалось создать список.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (id) => {
    setConfirmDeleteListId(id);
  };

  const handleConfirmDelete = async () => {
    if (confirmDeleteListId === null) return;

    setDeletingId(confirmDeleteListId);
    try {
      await api.deleteList(confirmDeleteListId);
      setConfirmDeleteListId(null);
      await loadLists();
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось удалить список.'));
    } finally {
      setDeletingId(null);
    }
  };

  const listToDelete = lists.find((list) => list.id === confirmDeleteListId);
  const isDeleteSubmitting = confirmDeleteListId !== null && deletingId === confirmDeleteListId;

  return (
    <div className="lists-page">
      <h2>Мои списки покупок</h2>
      {error && <div className="error">{error}</div>}

      <form onSubmit={handleCreate} className="create-form">
        <input
          type="text"
          placeholder="Например: Продукты на неделю"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (fieldErrors.title) {
              setFieldErrors((prev) => ({ ...prev, title: null }));
            }
          }}
        />
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Создаем...' : 'Создать'}
        </button>
      </form>
      {fieldErrors.title && <p className="field-error form-field-error">{fieldErrors.title}</p>}

      {loading ? (
        <p className="loading-inline">Загружаем списки...</p>
      ) : lists.length === 0 ? (
        <p className="empty">Списков пока нет. Создайте первый!</p>
      ) : (
        <ul className="lists">
          {lists.map((list) => (
            <li key={list.id} className="list-card">
              <Link to={`/lists/${list.id}`} className="list-card-link">
                <span className="list-title">{list.title}</span>
                <span className="list-date">{new Date(list.created_at).toLocaleDateString('ru-RU')}</span>
              </Link>
              <button
                onClick={() => handleDelete(list.id)}
                className="btn btn-danger btn-sm"
                disabled={deletingId === list.id}
              >
                {deletingId === list.id ? '...' : '✕'}
              </button>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={confirmDeleteListId !== null}
        title="Удалить список?"
        description={
          listToDelete
            ? `Список «${listToDelete.title}» будет удален без возможности восстановления.`
            : 'Список будет удален без возможности восстановления.'
        }
        confirmText="Удалить список"
        loadingText="Удаляем список..."
        loading={isDeleteSubmitting}
        onCancel={() => setConfirmDeleteListId(null)}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
}
