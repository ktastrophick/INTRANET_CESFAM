document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('chatFloatingBtn');
  const panel = document.getElementById('chatPanel');
  const chatList = document.getElementById('chatList');
  const chatWindow = document.getElementById('chatWindow');
  const backToList = document.getElementById('backToList');
  const chatWith = document.getElementById('chatWith');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');

  // seguridad: si faltan elementos, salir sin errores
  if (!btn || !panel) return;

  btn.addEventListener('click', () => {
    const isOpen = panel.style.display === 'flex';
    panel.style.display = isOpen ? 'none' : 'flex';
    panel.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
  });

  // si no hay lista o ventana, terminar
  if (!chatList || !chatWindow) return;

  // abrir chat individual al click en item
  document.querySelectorAll('.chat-list-item').forEach(item => {
    item.addEventListener('click', () => {
      const userNameEl = item.querySelector('h5');
      const userName = userNameEl ? userNameEl.innerText : 'Usuario';
      chatWith.textContent = userName;

      chatList.style.display = 'none';
      chatWindow.style.display = 'flex';
      chatWindow.setAttribute('aria-hidden', 'false');
    });
  });

  // volver a lista
  if (backToList) {
    backToList.addEventListener('click', () => {
      chatWindow.style.display = 'none';
      chatList.style.display = 'block';
      chatWindow.setAttribute('aria-hidden', 'true');
    });
  }

  // enviar
  function sendMessage() {
    if (!chatInput || !chatMessages) return;
    const text = chatInput.value.trim();
    if (!text) return;
    const msg = document.createElement('div');
    msg.className = 'message you';
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    chatInput.value = '';
  }

  if (sendBtn) sendBtn.addEventListener('click', sendMessage);
  if (chatInput) chatInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
});
