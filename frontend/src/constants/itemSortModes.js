export const ITEM_SORT_QUERY_PARAM = 'items_sort';

export const ITEM_SORT_MODE = {
  manual: 'manual',
  uncheckedFirst: 'unchecked_first',
  nameAsc: 'name_asc',
};

export const ITEM_SORT_OPTIONS = [
  { mode: ITEM_SORT_MODE.manual, label: 'Ручной порядок' },
  { mode: ITEM_SORT_MODE.uncheckedFirst, label: 'Неотмеченные сверху' },
  { mode: ITEM_SORT_MODE.nameAsc, label: 'По названию А-Я' },
];

const VALID_SORT_MODES = new Set(Object.values(ITEM_SORT_MODE));

export function normalizeItemSortMode(mode) {
  if (mode && VALID_SORT_MODES.has(mode)) {
    return mode;
  }

  return ITEM_SORT_MODE.manual;
}
