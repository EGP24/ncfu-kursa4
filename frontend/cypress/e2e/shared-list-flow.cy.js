describe('Shared list flow', () => {
  it('opens shared list and adds item', () => {
    cy.intercept('GET', '/api/shared/share-123', {
      statusCode: 200,
      body: {
        id: 40,
        title: 'Общая корзина',
        items: [],
      },
    }).as('getShared');

    cy.intercept('POST', '/api/lists/40/items?share_token=share-123', {
      statusCode: 200,
      body: {
        id: 401,
        name: 'Хлеб',
        quantity: 1,
        unit: 'шт',
        checked: false,
        position: 0,
      },
    }).as('createSharedItem');

    cy.intercept('GET', '/api/lists/40/history*', {
      statusCode: 200,
      body: [],
    });

    cy.visit('/shared/share-123', {
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

    cy.wait('@getShared');
    cy.contains('h2', 'Общая корзина').should('be.visible');

    cy.get('input[placeholder="Название товара..."]').type('Хлеб');
    cy.get('input[placeholder="ед."]').type('шт');
    cy.contains('button', 'Добавить').click();

    cy.wait('@createSharedItem').its('request.body').should('deep.equal', {
      name: 'Хлеб',
      quantity: 1,
      unit: 'шт',
    });
  });
});
