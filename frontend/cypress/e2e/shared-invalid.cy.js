describe('Shared invalid link', () => {
  it('shows error for invalid share token', () => {
    cy.intercept('GET', '/api/shared/bad-token', {
      statusCode: 404,
      body: 'List not found',
    }).as('getShared');

    cy.visit('/shared/bad-token');

    cy.wait('@getShared');
    cy.contains('h2', 'Список не найден').should('be.visible');
  });
});
