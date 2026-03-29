function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

describe('Core user flow', () => {
  it('logs in, adds item and opens history', () => {
    const token = createTestJwt({ user_id: 1, username: 'demo' });

    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        token,
        user: { id: 1, username: 'demo' },
      },
    }).as('login');

    cy.intercept('GET', '/api/lists', {
      statusCode: 200,
      body: [
        {
          id: 10,
          title: 'Личный бюджет',
          created_at: '2026-03-01T10:00:00.000Z',
        },
      ],
    }).as('getLists');

    cy.intercept('GET', '/api/lists/10', {
      statusCode: 200,
      body: {
        id: 10,
        title: 'Личный бюджет',
        share_token: null,
        items: [],
      },
    }).as('getList');

    cy.intercept('POST', '/api/lists/10/items', {
      statusCode: 200,
      body: {
        id: 200,
        name: 'Капучино',
        quantity: 2,
        unit: 'шт',
        position: 0,
        checked: false,
      },
    }).as('createItem');

    cy.intercept('GET', '/api/lists/10/history*', {
      statusCode: 200,
      body: [
        {
          id: 300,
          action: 'item_added',
          item_name: 'Капучино',
          details: 'Количество: 2; Ед.: шт',
          username: 'demo',
          created_at: '2026-03-01T10:05:00.000Z',
        },
      ],
    }).as('getHistory');

    cy.visit('/login', {
      onBeforeLoad(win) {
        class FakeWebSocket {
          constructor() {
            this.readyState = 1;
          }

          close() {}

          send() {}
        }

        win.WebSocket = FakeWebSocket;
      },
    });

    cy.contains('h2', 'Вход в аккаунт').should('be.visible');
    cy.get('#login-username').type('demo');
    cy.get('#login-password').type('secret123');
    cy.contains('button', 'Войти').click();

    cy.wait('@login');
    cy.wait('@getLists');
    cy.contains('h2', 'Мои списки покупок').should('be.visible');

    cy.contains('Личный бюджет').click();
    cy.wait('@getList');
    cy.contains('h2', 'Личный бюджет').should('be.visible');

    cy.get('input[placeholder="Название товара..."]').type('Капучино');
    cy.get('input[placeholder="ед."]').type('шт');
    cy.contains('button', 'Добавить').click();

    cy.wait('@createItem').its('request.body').should('deep.equal', {
      name: 'Капучино',
      quantity: 1,
      unit: 'шт',
    });

    cy.contains('button', 'История изменений').click();
    cy.wait('@getHistory');
    cy.contains('Капучино').should('be.visible');
    cy.contains('demo').should('be.visible');
  });
});
