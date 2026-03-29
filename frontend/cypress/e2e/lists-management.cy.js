function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

function loginAsDemo() {
  const token = createTestJwt({ user_id: 1, username: 'demo' });

  cy.intercept('POST', '/api/auth/login', {
    statusCode: 200,
    body: {
      token,
      user: { id: 1, username: 'demo' },
    },
  }).as('login');

  cy.visit('/login');
  cy.get('#login-username').type('demo');
  cy.get('#login-password').type('secret123');
  cy.contains('button', 'Войти').click();
  cy.wait('@login');
}

describe('Lists management', () => {
  it('creates a new list', () => {
    let listsRequestCount = 0;

    cy.intercept('GET', '/api/lists', (req) => {
      listsRequestCount += 1;

      if (listsRequestCount === 1) {
        req.reply({ statusCode: 200, body: [] });
        return;
      }

      req.reply({
        statusCode: 200,
        body: [
          {
            id: 77,
            title: 'Коммуналка',
            created_at: '2026-03-01T10:00:00.000Z',
          },
        ],
      });
    }).as('getLists');

    cy.intercept('POST', '/api/lists', {
      statusCode: 200,
      body: { id: 77, title: 'Коммуналка' },
    }).as('createList');

    loginAsDemo();
    cy.wait('@getLists');

    cy.get('input[placeholder="Например: Продукты на неделю"]').type('  Коммуналка  ');
    cy.contains('button', 'Создать').click();

    cy.wait('@createList').its('request.body').should('deep.equal', {
      title: 'Коммуналка',
    });
    cy.wait('@getLists');
    cy.contains('Коммуналка').should('be.visible');
  });

  it('deletes list after confirmation', () => {
    let listsRequestCount = 0;

    cy.intercept('GET', '/api/lists', (req) => {
      listsRequestCount += 1;

      if (listsRequestCount === 1) {
        req.reply({
          statusCode: 200,
          body: [
            {
              id: 77,
              title: 'Удаляемый список',
              created_at: '2026-03-01T10:00:00.000Z',
            },
          ],
        });
        return;
      }

      req.reply({ statusCode: 200, body: [] });
    }).as('getLists');

    cy.intercept('DELETE', '/api/lists/77', {
      statusCode: 204,
      body: null,
    }).as('deleteList');

    loginAsDemo();
    cy.wait('@getLists');

    cy.contains('.list-card', 'Удаляемый список').within(() => {
      cy.get('button.btn-danger').click();
    });

    cy.contains('button', 'Удалить список').click();
    cy.wait('@deleteList');
    cy.wait('@getLists');

    cy.contains('Списков пока нет. Создайте первый!').should('be.visible');
  });
});
