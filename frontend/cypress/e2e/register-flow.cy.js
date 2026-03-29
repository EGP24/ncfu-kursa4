function createTestJwt(payload) {
  const base64Url = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');

  return `header.${base64Url}.signature`;
}

describe('Register flow', () => {
  it('registers and redirects to lists', () => {
    const token = createTestJwt({ user_id: 8, username: 'new-user' });

    cy.intercept('POST', '/api/auth/register', {
      statusCode: 200,
      body: {
        token,
        user: { id: 8, username: 'new-user' },
      },
    }).as('register');

    cy.intercept('GET', '/api/lists', {
      statusCode: 200,
      body: [],
    }).as('getLists');

    cy.visit('/register');

    cy.get('#register-username').type('new-user');
    cy.get('#register-password').type('secret123');
    cy.get('#register-password-repeat').type('secret123');
    cy.contains('button', 'Зарегистрироваться').click();

    cy.wait('@register');
    cy.wait('@getLists');
    cy.contains('h2', 'Мои списки покупок').should('be.visible');
  });
});
