import { ApiError, api, getErrorMessage, getFieldErrors } from '../api';

function mockJsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {
      get: () => 'application/json',
    },
    json: async () => body,
    text: async () => JSON.stringify(body),
  };
}

describe('api module', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('calls login endpoint with expected payload', async () => {
    fetch.mockResolvedValue(
      mockJsonResponse({ token: 'jwt.token.sign', user: { id: 1, username: 'demo' } }),
    );

    const result = await api.login('demo', 'secret123');

    expect(result.user.username).toBe('demo');
    expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'demo', password: 'secret123' }),
    });
  });

  it('builds history query with share token and actions', async () => {
    fetch.mockResolvedValue(mockJsonResponse([]));

    await api.getHistory(5, {
      shareToken: 'share-1',
      actions: ['item_added', 'item_deleted'],
    });

    expect(fetch).toHaveBeenCalledWith(
      '/api/lists/5/history?share_token=share-1&actions=item_added&actions=item_deleted',
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('maps backend validation error to ApiError fieldErrors', async () => {
    fetch.mockResolvedValue(
      mockJsonResponse(
        {
          error: 'validation_error',
          details: [
            { instance_path: '/username', message: 'must NOT have fewer than 3 characters' },
          ],
        },
        400,
      ),
    );

    await expect(api.register('ab', '123456')).rejects.toBeInstanceOf(ApiError);

    try {
      await api.register('ab', '123456');
    } catch (error) {
      expect(getFieldErrors(error)).toEqual({ username: 'must NOT have fewer than 3 characters' });
      expect(getErrorMessage(error)).toBe('Проверьте правильность заполнения полей.');
    }
  });
});
