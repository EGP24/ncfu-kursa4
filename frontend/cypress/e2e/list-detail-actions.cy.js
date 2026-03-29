function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

function loginAndOpenList({ listDetails }) {
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
    body: listDetails,
  }).as('getList');

  cy.visit('/login');
  cy.get('#login-username').type('demo');
  cy.get('#login-password').type('secret123');
  cy.contains('button', 'Войти').click();

  cy.wait('@login');
  cy.wait('@getLists');

  cy.contains('Личный бюджет').click();
  cy.wait('@getList');
  cy.contains('h2', 'Личный бюджет').should('be.visible');
}

describe('List details actions', () => {
  it('sorts items by name', () => {
    cy.intercept('PUT', '/api/lists/10/items/sort', {
      statusCode: 200,
      body: [
        {
          id: 2,
          name: 'Бананы',
          quantity: 2,
          unit: 'кг',
          checked: false,
          position: 0,
        },
        {
          id: 1,
          name: 'Яблоки',
          quantity: 1,
          unit: 'кг',
          checked: false,
          position: 1,
        },
      ],
    }).as('sortItems');

    loginAndOpenList({
      listDetails: {
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
            quantity: 2,
            unit: 'кг',
            checked: false,
            position: 1,
          },
        ],
      },
    });

    cy.contains('button', 'По названию А-Я').click();
    cy.wait('@sortItems').its('request.body').should('deep.equal', { mode: 'name_asc' });
  });

  it('shares and unshares list', () => {
    cy.intercept('POST', '/api/lists/10/share', {
      statusCode: 200,
      body: { share_token: 'share-abc' },
    }).as('shareList');

    cy.intercept('DELETE', '/api/lists/10/share', {
      statusCode: 204,
      body: null,
    }).as('unshareList');

    loginAndOpenList({
      listDetails: {
        id: 10,
        title: 'Личный бюджет',
        share_token: null,
        items: [],
      },
    });

    cy.contains('button', 'Поделиться списком').click();
    cy.wait('@shareList');

    cy.get('.share-link-text')
      .should('have.attr', 'href')
      .and('include', '/shared/share-abc');

    cy.contains('button', 'Отключить').click();
    cy.wait('@unshareList');
    cy.contains('button', 'Поделиться списком').should('be.visible');
  });

  it('opens history and sends action filters in request', () => {
    cy.intercept('GET', '/api/lists/10/history*', {
      statusCode: 200,
      body: [],
    }).as('getHistory');

    loginAndOpenList({
      listDetails: {
        id: 10,
        title: 'Личный бюджет',
        share_token: null,
        items: [],
      },
    });

    cy.contains('button', 'История изменений').click();
    cy.wait('@getHistory');

    cy.contains('.history-filter-chip', 'Добавлен').click();

    cy.get('@getHistory.all').should((calls) => {
      const hasFilteredRequest = calls.some((call) => call.request.url.includes('actions='));
      expect(hasFilteredRequest).to.equal(true);
    });
  });
});
