describe('Auth validation and errors', () => {
  it('shows client validation error for whitespace username', () => {
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {},
    }).as('login');

    cy.visit('/login');
    cy.get('#login-username').type('   ');
    cy.get('#login-password').type('secret123');
    cy.contains('button', 'Войти').click();

    cy.contains('Введите имя пользователя.').should('be.visible');
    cy.get('@login.all').should('have.length', 0);
  });

  it('shows backend auth error for invalid credentials', () => {
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: 'Invalid credentials',
    }).as('login');

    cy.visit('/login');
    cy.get('#login-username').type('demo');
    cy.get('#login-password').type('wrong-password');
    cy.contains('button', 'Войти').click();

    cy.wait('@login');
    cy.contains('Неверный логин или пароль.').should('be.visible');
  });

  it('shows client validation error when register passwords mismatch', () => {
    cy.intercept('POST', '/api/auth/register', {
      statusCode: 200,
      body: {},
    }).as('register');

    cy.visit('/register');
    cy.get('#register-username').type('new-user');
    cy.get('#register-password').type('secret123');
    cy.get('#register-password-repeat').type('secret124');
    cy.contains('button', 'Зарегистрироваться').click();

    cy.contains('Пароли не совпадают.').should('be.visible');
    cy.get('@register.all').should('have.length', 0);
  });
});
