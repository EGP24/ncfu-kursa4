function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

function loginWithListsResponse(listsBody) {
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
    body: listsBody,
  }).as('getLists');

  cy.visit('/login');
  cy.get('#login-username').type('demo');
  cy.get('#login-password').type('secret123');
  cy.contains('button', 'Войти').click();

  cy.wait('@login');
  cy.wait('@getLists');
}

describe('Error handling', () => {
  it('shows backend error when list creation fails', () => {
    cy.intercept('POST', '/api/lists', {
      statusCode: 500,
      body: { message: 'Не удалось создать список (тест).' },
    }).as('createList');

    loginWithListsResponse([]);

    cy.get('input[placeholder="Например: Продукты на неделю"]').type('Новый список');
    cy.contains('button', 'Создать').click();

    cy.wait('@createList');
    cy.contains('Не удалось создать список (тест).').should('be.visible');
  });

  it('shows backend error when list deletion fails', () => {
    cy.intercept('DELETE', '/api/lists/55', {
      statusCode: 403,
      body: { message: 'Недостаточно прав (тест).' },
    }).as('deleteList');

    loginWithListsResponse([
      {
        id: 55,
        title: 'Список без прав',
        created_at: '2026-03-01T10:00:00.000Z',
      },
    ]);

    cy.contains('.list-card', 'Список без прав').within(() => {
      cy.get('button.btn-danger').click();
    });

    cy.contains('button', 'Удалить список').click();
    cy.wait('@deleteList');
    cy.contains('Недостаточно прав (тест).').should('be.visible');
  });
});
