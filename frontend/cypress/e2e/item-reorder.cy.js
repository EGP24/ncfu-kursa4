function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

describe('Item reorder', () => {
  it('sends move request after drag and drop reorder', () => {
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
        items: [
          {
            id: 1,
            name: 'Яблоки',
            quantity: 1,
            unit: 'кг',
            checked: false,
            position: 0,
          },
          {
            id: 2,
            name: 'Бананы',
            quantity: 1,
            unit: 'кг',
            checked: false,
            position: 1,
          },
        ],
      },
    }).as('getList');

    cy.intercept('PUT', '/api/lists/10/items/1/position', {
      statusCode: 200,
      body: null,
    }).as('moveItem');

    cy.visit('/login');
    cy.get('#login-username').type('demo');
    cy.get('#login-password').type('secret123');
    cy.contains('button', 'Войти').click();

    cy.wait('@login');
    cy.wait('@getLists');
    cy.contains('Личный бюджет').click();
    cy.wait('@getList');

    cy.contains('.item-row', 'Яблоки').as('sourceRow');
    cy.contains('.item-row', 'Бананы').as('targetRow');

    cy.window().then((win) => {
      const dataTransfer = new win.DataTransfer();

      cy.get('@sourceRow').trigger('dragstart', { dataTransfer });
      cy.get('@targetRow').trigger('dragover', { dataTransfer });
      cy.get('@sourceRow').trigger('dragend', { dataTransfer });
    });

    cy.wait('@moveItem').its('request.body').should('deep.equal', { position: 1 });
  });
});
