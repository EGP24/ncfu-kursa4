Cypress.on('window:before:load', (win) => {
  class FakeWebSocket {
    constructor() {
      this.readyState = 1;
    }

    close() {}

    send() {}
  }

  win.WebSocket = FakeWebSocket;
});
