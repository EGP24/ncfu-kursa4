function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

function loginAndOpenListWithItems(items) {
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
      items,
    },
  }).as('getList');

  cy.visit('/login');
  cy.get('#login-username').type('demo');
  cy.get('#login-password').type('secret123');
  cy.contains('button', 'Войти').click();

  cy.wait('@login');
  cy.wait('@getLists');
  cy.contains('Личный бюджет').click();
  cy.wait('@getList');
}

describe('Item edit actions', () => {
  it('sends update payload on item save', () => {
    cy.intercept('PUT', '/api/lists/10/items/1', {
      statusCode: 200,
      body: {
        id: 1,
        name: 'Сыр',
        quantity: 2,
        unit: 'кг',
        checked: false,
        position: 0,
      },
    }).as('updateItem');

    loginAndOpenListWithItems([
      {
        id: 1,
        name: 'Молоко',
        quantity: 1,
        unit: 'л',
        checked: false,
        position: 0,
      },
    ]);

    cy.contains('.item-row', 'Молоко').within(() => {
      cy.contains('button', '✎').click();
    });

    cy.get('.item-row.editing input.item-name-input').clear().type('Сыр');
    cy.get('.item-row.editing input.item-qty-input').clear().type('2');
    cy.get('.item-row.editing input.item-unit-input').clear().type('кг');
    cy.get('.item-row.editing').contains('button', '✓').click();

    cy.wait('@updateItem').its('request.body').should('deep.equal', {
      name: 'Сыр',
      quantity: 2,
      unit: 'кг',
    });
  });

  it('cancels edit without update request', () => {
    cy.intercept('PUT', '/api/lists/10/items/1', {
      statusCode: 200,
      body: {},
    }).as('updateItem');

    loginAndOpenListWithItems([
      {
        id: 1,
        name: 'Молоко',
        quantity: 1,
        unit: 'л',
        checked: false,
        position: 0,
      },
    ]);

    cy.contains('.item-row', 'Молоко').within(() => {
      cy.contains('button', '✎').click();
    });

    cy.get('.item-row.editing input.item-name-input').clear().type('Не сохранить');
    cy.get('.item-row.editing').contains('button', '✕').click();

    cy.get('@updateItem.all').should('have.length', 0);
  });
});
