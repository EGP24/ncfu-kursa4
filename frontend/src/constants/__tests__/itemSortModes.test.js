import {
  ITEM_SORT_MODE,
  ITEM_SORT_OPTIONS,
  ITEM_SORT_QUERY_PARAM,
  normalizeItemSortMode,
} from '../itemSortModes';

describe('item sort modes', () => {
  it('exports query param and options', () => {
    expect(ITEM_SORT_QUERY_PARAM).toBe('items_sort');
    expect(ITEM_SORT_OPTIONS).toHaveLength(3);
  });

  it('normalizes mode to manual for invalid values', () => {
    expect(normalizeItemSortMode(ITEM_SORT_MODE.nameAsc)).toBe(ITEM_SORT_MODE.nameAsc);
    expect(normalizeItemSortMode('bad-value')).toBe(ITEM_SORT_MODE.manual);
    expect(normalizeItemSortMode(null)).toBe(ITEM_SORT_MODE.manual);
  });
});
