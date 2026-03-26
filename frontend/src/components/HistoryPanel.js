import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api, getErrorMessage } from '../api';

const ACTION_META = {
  item_added: {
    label: 'Добавлен',
    icon: '+',
    tone: 'added',
  },
  item_edited: {
    label: 'Изменен',
    icon: '✎',
    tone: 'edited',
  },
  item_deleted: {
    label: 'Удален',
    icon: '−',
    tone: 'deleted',
  },
  item_checked: {
    label: 'Отмечен',
    icon: '✓',
    tone: 'checked',
  },
  item_unchecked: {
    label: 'Снята отметка',
    icon: '↺',
    tone: 'unchecked',
  },
};

const ACTION_ORDER = ['item_added', 'item_edited', 'item_deleted', 'item_checked', 'item_unchecked'];
const KNOWN_ACTIONS = new Set(ACTION_ORDER);
const HISTORY_ACTION_PARAM = 'history_action';

function normalizeActions(actions) {
  const raw = Array.isArray(actions) ? actions : [];
  const selected = ACTION_ORDER.filter((action) => raw.includes(action));
  return selected.length > 0 ? selected : ACTION_ORDER;
}

function normalizeDetails(details) {
  return String(details || '').replace(/;\s+/g, '\n');
}

export default function HistoryPanel({ listId, shareToken, historyKey }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [history, setHistory] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState('');

  const selectedActions = useMemo(
    () => normalizeActions(searchParams.getAll(HISTORY_ACTION_PARAM)),
    [searchParams],
  );
  const hasCustomFilter = searchParams.getAll(HISTORY_ACTION_PARAM).length > 0;
  const isAllActionsSelected = selectedActions.length === ACTION_ORDER.length;

  const requestActions = isAllActionsSelected && !hasCustomFilter ? undefined : selectedActions;

  const loadHistory = async ({ silent = false } = {}) => {
    const showBlockingLoader = !silent && !hasLoaded && history.length === 0;

    if (showBlockingLoader) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }

    try {
      const data = await api.getHistory(listId, { shareToken, actions: requestActions });
      setHistory(data);
      setError('');
      setHasLoaded(true);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось загрузить историю изменений.'));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleToggle = () => {
    const next = !open;
    setOpen(next);
    if (!next) return;

    if (!hasLoaded) {
      loadHistory();
      return;
    }

    loadHistory({ silent: true });
  };

  // Auto-reload when historyKey changes (from WebSocket) and panel is open
  useEffect(() => {
    if (open && historyKey > 0) {
      loadHistory({ silent: true });
    }
  }, [historyKey, open, requestActions]);

  useEffect(() => {
    if (!open || !hasLoaded) {
      return;
    }

    loadHistory({ silent: true });
  }, [selectedActions, open, hasLoaded]);

  const writeActionFiltersToQuery = (actions) => {
    const normalizedActions = normalizeActions(actions);

    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete(HISTORY_ACTION_PARAM);

      if (normalizedActions.length !== ACTION_ORDER.length) {
        normalizedActions.forEach((action) => next.append(HISTORY_ACTION_PARAM, action));
      }

      return next;
    });
  };

  const resetFilters = () => {
    writeActionFiltersToQuery(ACTION_ORDER);
  };

  const toggleActionFilter = (action) => {
    if (!KNOWN_ACTIONS.has(action)) {
      return;
    }

    const isSelected = selectedActions.includes(action);
    if (isSelected && selectedActions.length === 1) {
      return;
    }

    const nextActions = isSelected
      ? selectedActions.filter((value) => value !== action)
      : [...selectedActions, action].sort((left, right) => ACTION_ORDER.indexOf(left) - ACTION_ORDER.indexOf(right));

    writeActionFiltersToQuery(nextActions);
  };

  return (
    <div className="history-panel">
      <div className="history-header">
        <button className="btn btn-sm" onClick={handleToggle}>
          {open ? 'Скрыть историю' : 'История изменений'}
        </button>
        {open && refreshing && <span className="history-updating">Обновляем...</span>}
      </div>

      {open && (
        <>
          <div className="history-filters">
            <button
              type="button"
              className={`history-filter-chip history-filter-all ${isAllActionsSelected ? 'active' : ''}`}
              onClick={resetFilters}
            >
              <span className="history-filter-label">Все</span>
            </button>

            {ACTION_ORDER.map((action) => {
              const meta = ACTION_META[action];
              const active = selectedActions.includes(action);

              return (
                <button
                  key={action}
                  type="button"
                  className={`history-filter-chip history-filter-${meta.tone} ${active ? 'active' : ''}`}
                  onClick={() => toggleActionFilter(action)}
                >
                  <span className="history-filter-icon">{meta.icon}</span>
                  <span className="history-filter-label">{meta.label}</span>
                </button>
              );
            })}
          </div>

          <div className="history-list">
            {error && <p className="field-error history-error">{error}</p>}
            {loading && <p className="history-loading">Загрузка...</p>}
            {!loading && history.length === 0 && (
              <p className="history-empty">
                {isAllActionsSelected ? 'История пуста' : 'По выбранным фильтрам записей нет'}
              </p>
            )}
            {!loading && history.map((h) => (
              <div key={h.id} className="history-item">
                <div className="history-top">
                  <span className={`history-action-badge history-action-${ACTION_META[h.action]?.tone || 'default'}`}>
                    <span className="history-action-icon">{ACTION_META[h.action]?.icon || '•'}</span>
                    <span className="history-action-label">{ACTION_META[h.action]?.label || h.action}</span>
                  </span>
                  <span className="history-item-name">{h.item_name}</span>
                </div>
                {h.details && <div className="history-details">{normalizeDetails(h.details)}</div>}
                <div className="history-meta">
                  <span className="history-user">{h.username}</span>
                  <span className="history-date">
                    {new Date(h.created_at).toLocaleString('ru-RU', {
                      day: '2-digit', month: '2-digit', year: 'numeric',
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
