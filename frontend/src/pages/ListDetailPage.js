import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { api, connectWebSocket, getErrorMessage, getFieldErrors } from '../api';
import { useAuth } from '../AuthContext';
import ConfirmDialog from '../components/ConfirmDialog';
import ItemRow from '../components/ItemRow';
import HistoryPanel from '../components/HistoryPanel';
import {
  ITEM_SORT_MODE,
  ITEM_SORT_OPTIONS,
  ITEM_SORT_QUERY_PARAM,
  normalizeItemSortMode,
} from '../constants/itemSortModes';
import { COMMON_UNIT_SUGGESTIONS } from '../constants/units';
import { hasErrors, trimPayload, validateItemPayload, validateListTitle } from '../validation';


const UNIT_DATALIST_ID = 'list-item-unit-suggestions';


function sortItemsByPosition(items) {
  return [...items].sort((left, right) => {
    if (left.position !== right.position) {
      return left.position - right.position;
    }
    return left.id - right.id;
  });
}

function reorderItems(items, draggedItemId, targetItemId) {
  if (draggedItemId === targetItemId) {
    return items;
  }

  const fromIndex = items.findIndex((item) => item.id === draggedItemId);
  const toIndex = items.findIndex((item) => item.id === targetItemId);
  if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) {
    return items;
  }

  const next = [...items];
  const [movedItem] = next.splice(fromIndex, 1);
  next.splice(toIndex, 0, movedItem);

  return next.map((item, index) => ({ ...item, position: index }));
}

function buildItemsByOrder(items, orderedIds) {
  const itemsById = new Map(items.map((item) => [item.id, item]));
  const orderedItems = orderedIds
    .map((id, index) => {
      const item = itemsById.get(id);
      if (!item) return null;
      return { ...item, position: index };
    })
    .filter(Boolean);

  const orderedIdsSet = new Set(orderedIds);
  const extraItems = sortItemsByPosition(items.filter((item) => !orderedIdsSet.has(item.id))).map((item, index) => ({
    ...item,
    position: orderedItems.length + index,
  }));

  return [...orderedItems, ...extraItems];
}

export default function ListDetailPage() {
  const { id } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const { token } = useAuth();
  const [list, setList] = useState(null);
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [shareLink, setShareLink] = useState('');
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState('');
  const [titleError, setTitleError] = useState('');
  const [titleSaving, setTitleSaving] = useState(false);

  // New item form
  const [newName, setNewName] = useState('');
  const [newQty, setNewQty] = useState(1);
  const [newUnit, setNewUnit] = useState('');
  const [itemFormErrors, setItemFormErrors] = useState({});
  const [creatingItem, setCreatingItem] = useState(false);
  const [sortingItems, setSortingItems] = useState(false);
  const [confirmDeleteItemId, setConfirmDeleteItemId] = useState(null);
  const [deletingItemId, setDeletingItemId] = useState(null);
  const [draggingItemId, setDraggingItemId] = useState(null);
  const [reorderSaving, setReorderSaving] = useState(false);
  const [copied, setCopied] = useState(false);

  const wsRef = useRef(null);
  const itemsRef = useRef(items);
  const dragStartOrderRef = useRef([]);
  const [historyKey, setHistoryKey] = useState(0);

  const selectedSortMode = normalizeItemSortMode(searchParams.get(ITEM_SORT_QUERY_PARAM));

  useEffect(() => {
    itemsRef.current = items;
  }, [items]);

  const setSortModeInQuery = useCallback((mode) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set(ITEM_SORT_QUERY_PARAM, mode);
      return next;
    });
  }, [setSearchParams]);

  const loadList = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const data = await api.getList(id);
      setList(data);
      setItems(sortItemsByPosition(data.items));
      setTitleDraft(data.title);
      if (data.share_token) {
        setShareLink(`${window.location.origin}/shared/${data.share_token}`);
      } else {
        setShareLink('');
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось загрузить список.'));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadList();
  }, [loadList]);

  // WebSocket
  useEffect(() => {
    if (!list) return;
    const ws = connectWebSocket(list.id, {
      token,
      shareToken: list.share_token,
      onMessage: (msg) => {
        if (msg.type === 'item_added') {
          setItems((prev) => {
            if (prev.some((i) => i.id === msg.item.id)) return prev;
            return sortItemsByPosition([...prev, msg.item]);
          });
        } else if (msg.type === 'item_updated') {
          setItems((prev) => sortItemsByPosition(prev.map((i) => (i.id === msg.item.id ? msg.item : i))));
        } else if (msg.type === 'item_deleted') {
          setItems((prev) => prev.filter((i) => i.id !== msg.item_id));
        } else if (msg.type === 'history_updated') {
          setHistoryKey((k) => k + 1);
        }
      },
    });
    wsRef.current = ws;
    return () => ws.close();
  }, [list?.id, list?.share_token, token]);

  const handleAddItem = async (e) => {
    e.preventDefault();

    const payload = trimPayload({ name: newName, quantity: newQty, unit: newUnit });
    const validationErrors = validateItemPayload(payload);
    if (hasErrors(validationErrors)) {
      setItemFormErrors(validationErrors);
      return;
    }

    const requestPayload = {
      ...payload,
      quantity: Number(payload.quantity),
      unit: payload.unit || null,
    };

    setItemFormErrors({});
    setCreatingItem(true);

    try {
      await api.createItem(id, requestPayload);
      setNewName('');
      setNewQty(1);
      setNewUnit('');
    } catch (err) {
      const backendFieldErrors = getFieldErrors(err);
      if (hasErrors(backendFieldErrors)) {
        setItemFormErrors((prev) => ({ ...prev, ...backendFieldErrors }));
      }
      setError(getErrorMessage(err, 'Не удалось добавить элемент.'));
    } finally {
      setCreatingItem(false);
    }
  };

  const handleUpdateItem = async (itemId, data) => {
    try {
      await api.updateItem(id, itemId, data);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось обновить элемент.'));
      throw err;
    }
  };

  const handleDeleteItem = (itemId) => {
    setConfirmDeleteItemId(itemId);
  };

  const handleConfirmDeleteItem = async () => {
    if (confirmDeleteItemId === null) return;

    setDeletingItemId(confirmDeleteItemId);
    try {
      await api.deleteItem(id, confirmDeleteItemId);
      setConfirmDeleteItemId(null);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось удалить элемент.'));
    } finally {
      setDeletingItemId(null);
    }
  };

  const handleToggleCheck = async (itemId, checked) => {
    try {
      await handleUpdateItem(itemId, { checked: !checked });
    } catch {
      // handled in handleUpdateItem
    }
  };

  const handleSortItems = async (mode) => {
    if (!list || sortingItems || reorderSaving) return;

    setSortingItems(true);
    try {
      const sortedItems = await api.sortItems(list.id, mode);
      setItems(sortItemsByPosition(sortedItems));
      setSortModeInQuery(mode);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось отсортировать элементы.'));
    } finally {
      setSortingItems(false);
    }
  };

  const handleItemDragStart = (event, itemId) => {
    if (reorderSaving) {
      event.preventDefault();
      return;
    }

    setDraggingItemId(itemId);
    dragStartOrderRef.current = itemsRef.current.map((item) => item.id);
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', String(itemId));
  };

  const handleItemDragOver = (event, targetItemId) => {
    event.preventDefault();
    if (reorderSaving) return;

    const rawDraggedItemId = event.dataTransfer.getData('text/plain');
    const draggedItemId = rawDraggedItemId ? Number(rawDraggedItemId) : draggingItemId;
    if (!draggedItemId) return;

    setItems((prev) => reorderItems(prev, draggedItemId, targetItemId));
  };

  const handleItemDragEnd = async () => {
    const movedItemId = draggingItemId;
    const startOrder = dragStartOrderRef.current;

    setDraggingItemId(null);
    dragStartOrderRef.current = [];

    if (!movedItemId || startOrder.length === 0 || !list) {
      return;
    }

    const currentOrder = itemsRef.current.map((item) => item.id);
    const oldIndex = startOrder.indexOf(movedItemId);
    const newIndex = currentOrder.indexOf(movedItemId);
    if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) {
      return;
    }

    setReorderSaving(true);
    try {
      await api.moveItem(list.id, movedItemId, newIndex);
      setSortModeInQuery(ITEM_SORT_MODE.manual);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось изменить порядок элементов.'));
      setItems((prev) => buildItemsByOrder(prev, startOrder));
    } finally {
      setReorderSaving(false);
    }
  };

  const handleShare = async () => {
    try {
      const res = await api.shareList(id);
      const link = `${window.location.origin}/shared/${res.share_token}`;
      setShareLink(link);
      setList((prev) => ({ ...prev, share_token: res.share_token }));
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось включить общий доступ.'));
    }
  };

  const handleUnshare = async () => {
    try {
      await api.unshareList(id);
      setShareLink('');
      setList((prev) => ({ ...prev, share_token: null }));
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось отключить общий доступ.'));
    }
  };

  const handleCopyLink = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareLink);
      } else {
        const textarea = document.createElement('textarea');
        textarea.value = shareLink;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
      }

      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      setError('Не удалось скопировать ссылку. Скопируйте ее вручную.');
    }
  };

  const handleTitleSave = async () => {
    const payload = trimPayload({ title: titleDraft });
    const validationErrors = validateListTitle(payload.title);
    if (hasErrors(validationErrors)) {
      setTitleError(validationErrors.title || 'Некорректное название списка.');
      return;
    }

    setTitleError('');
    setTitleSaving(true);

    try {
      await api.updateList(id, payload.title);
      setList((prev) => ({ ...prev, title: payload.title }));
      setEditingTitle(false);
    } catch (err) {
      const backendFieldErrors = getFieldErrors(err);
      if (backendFieldErrors.title) {
        setTitleError(backendFieldErrors.title);
      }
      setError(getErrorMessage(err, 'Не удалось обновить название списка.'));
    } finally {
      setTitleSaving(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  const itemToDelete = items.find((item) => item.id === confirmDeleteItemId);
  const isDeleteItemSubmitting = confirmDeleteItemId !== null && deletingItemId === confirmDeleteItemId;

  if (!list) {
    return (
      <div className="error-page">
        <h2>{error || 'Список не найден'}</h2>
      </div>
    );
  }

  return (
    <div className="list-detail">
      {error && <div className="error">{error}</div>}

      <div className="list-header">
        {editingTitle ? (
          <div className="title-edit">
            <input
              value={titleDraft}
              onChange={(e) => {
                setTitleDraft(e.target.value);
                if (titleError) setTitleError('');
              }}
            />
            <button className="btn btn-sm btn-primary" onClick={handleTitleSave} disabled={titleSaving}>
              {titleSaving ? '...' : '✓'}
            </button>
            <button
              className="btn btn-sm"
              onClick={() => {
                setEditingTitle(false);
                setTitleDraft(list.title);
                setTitleError('');
              }}
            >
              ✕
            </button>
          </div>
        ) : (
          <h2 onClick={() => setEditingTitle(true)} className="editable-title" title="Нажмите для редактирования">
            {list.title}
          </h2>
        )}
        {titleError && <p className="field-error">{titleError}</p>}
      </div>

      {/* Share section */}
      <div className="share-section">
        {shareLink ? (
          <div className="share-active">
            <div className="share-link-card">
              <span className="share-link-label">Ссылка для общего доступа</span>
              <a className="share-link-text" href={shareLink} target="_blank" rel="noreferrer">
                {shareLink}
              </a>
            </div>
            <div className="share-actions">
              <button className="btn btn-sm" onClick={handleCopyLink}>
                {copied ? 'Скопировано' : 'Копировать'}
              </button>
              <button className="btn btn-sm btn-danger" onClick={handleUnshare}>Отключить</button>
            </div>
          </div>
        ) : (
          <button className="btn btn-sm" onClick={handleShare}>Поделиться списком</button>
        )}
      </div>

      <div className="item-sort-controls">
        {ITEM_SORT_OPTIONS.map((option) => (
          <button
            key={option.mode}
            type="button"
            className={`item-sort-chip ${selectedSortMode === option.mode ? 'active' : ''}`}
            onClick={() => handleSortItems(option.mode)}
            disabled={sortingItems || reorderSaving}
          >
            {option.label}
          </button>
        ))}
      </div>

      {/* Add item form */}
      <form onSubmit={handleAddItem} className="add-item-form">
        <input
          type="text"
          placeholder="Название товара..."
          value={newName}
          onChange={(e) => {
            setNewName(e.target.value);
            if (itemFormErrors.name) {
              setItemFormErrors((prev) => ({ ...prev, name: null }));
            }
          }}
          className="item-name-input"
        />
        <input
          type="number"
          min="0.01"
          step="0.01"
          value={newQty}
          onChange={(e) => {
            setNewQty(e.target.value);
            if (itemFormErrors.quantity) {
              setItemFormErrors((prev) => ({ ...prev, quantity: null }));
            }
          }}
          className="item-qty-input"
        />
        <input
          type="text"
          placeholder="ед."
          value={newUnit}
          list={UNIT_DATALIST_ID}
          onChange={(e) => {
            setNewUnit(e.target.value);
            if (itemFormErrors.unit) {
              setItemFormErrors((prev) => ({ ...prev, unit: null }));
            }
          }}
          className="item-unit-input"
        />
        <button type="submit" className="btn btn-primary" disabled={creatingItem}>
          {creatingItem ? 'Добавляем...' : 'Добавить'}
        </button>
      </form>
      {(itemFormErrors.name || itemFormErrors.quantity || itemFormErrors.unit) && (
        <p className="field-error form-field-error">
          {itemFormErrors.name || itemFormErrors.quantity || itemFormErrors.unit}
        </p>
      )}

      {/* Items list */}
      <ul className="items-list">
        {items.length === 0 && <li className="empty">Список пуст</li>}
        {items.map((item) => (
          <ItemRow
            key={item.id}
            item={item}
            onToggle={() => handleToggleCheck(item.id, item.checked)}
            onUpdate={(data) => handleUpdateItem(item.id, data)}
            onDelete={() => handleDeleteItem(item.id)}
            unitSuggestionsId={UNIT_DATALIST_ID}
            dragEnabled={!creatingItem && !reorderSaving && !sortingItems}
            isDragging={draggingItemId === item.id}
            onDragStart={handleItemDragStart}
            onDragOver={handleItemDragOver}
            onDragEnd={handleItemDragEnd}
          />
        ))}
      </ul>

      <datalist id={UNIT_DATALIST_ID}>
        {COMMON_UNIT_SUGGESTIONS.map((unitOption) => (
          <option key={unitOption} value={unitOption} />
        ))}
      </datalist>

      {/* History */}
      <HistoryPanel listId={list.id} historyKey={historyKey} />

      <ConfirmDialog
        open={confirmDeleteItemId !== null}
        title="Удалить элемент?"
        description={
          itemToDelete
            ? `Элемент «${itemToDelete.name}» будет удален из списка без возможности восстановления.`
            : 'Элемент будет удален из списка без возможности восстановления.'
        }
        confirmText="Удалить элемент"
        loadingText="Удаляем элемент..."
        loading={isDeleteItemSubmitting}
        onCancel={() => setConfirmDeleteItemId(null)}
        onConfirm={handleConfirmDeleteItem}
      />
    </div>
  );
}
