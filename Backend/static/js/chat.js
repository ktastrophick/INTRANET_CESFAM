document.addEventListener('DOMContentLoaded', () => {
  // ========================================
  // ELEMENTOS DEL DOM
  // ========================================
  const btn = document.getElementById('chatFloatingBtn');
  const panel = document.getElementById('chatPanel');
  const chatList = document.getElementById('chatList');
  const chatWindow = document.getElementById('chatWindow');
  const backToList = document.getElementById('backToList');
  const chatWith = document.getElementById('chatWith');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');

  // Seguridad: si faltan elementos críticos, salir sin errores
  if (!btn || !panel) {
    console.warn('Chat: Elementos principales no encontrados');
    return;
  }

  // ========================================
  // TOGGLE PANEL PRINCIPAL
  // ========================================
  btn.addEventListener('click', () => {
    const isOpen = panel.getAttribute('aria-hidden') === 'false';
    
    if (isOpen) {
      // Cerrar panel
      panel.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-label', 'Abrir chat');
    } else {
      // Abrir panel
      panel.setAttribute('aria-hidden', 'false');
      btn.setAttribute('aria-label', 'Cerrar chat');
      
      // Asegurar que se muestra la lista al abrir
      if (chatList && chatWindow) {
        chatList.style.display = 'flex';
        chatWindow.setAttribute('aria-hidden', 'true');
      }
    }
  });

  // Si no hay lista o ventana, terminar aquí
  if (!chatList || !chatWindow) return;

  // ========================================
  // ABRIR CHAT INDIVIDUAL
  // ========================================
  document.querySelectorAll('.chat-list-item').forEach(item => {
    item.addEventListener('click', () => {
      // Obtener nombre del usuario
      const userNameEl = item.querySelector('.info h5');
      const userName = userNameEl ? userNameEl.textContent.trim() : 'Usuario';
      
      // Actualizar título del chat
      if (chatWith) {
        chatWith.textContent = userName;
      }

      // Cambiar de vista: ocultar lista, mostrar chat
      chatList.style.display = 'none';
      chatWindow.setAttribute('aria-hidden', 'false');
      
      // Limpiar mensajes anteriores (opcional)
      if (chatMessages) {
        chatMessages.innerHTML = '';
        
        // Agregar estado vacío (opcional)
        const emptyState = document.createElement('div');
        emptyState.className = 'chat-empty-state';
        emptyState.innerHTML = `
          <i class="fas fa-comments"></i>
          <p>Aún no hay mensajes.<br>¡Envía el primero!</p>
        `;
        chatMessages.appendChild(emptyState);
      }
      
      // Focus en input
      if (chatInput) {
        chatInput.focus();
      }
    });
  });

  // ========================================
  // VOLVER A LISTA
  // ========================================
  if (backToList) {
    backToList.addEventListener('click', () => {
      chatWindow.setAttribute('aria-hidden', 'true');
      chatList.style.display = 'flex';
    });
  }

  // ========================================
  // ENVIAR MENSAJE
  // ========================================
  function sendMessage() {
    if (!chatInput || !chatMessages) return;
    
    const text = chatInput.value.trim();
    if (!text) return;

    // Remover estado vacío si existe
    const emptyState = chatMessages.querySelector('.chat-empty-state');
    if (emptyState) {
      emptyState.remove();
    }

    // Crear elemento de mensaje
    const msg = document.createElement('div');
    msg.className = 'chat-message sent'; 
    
    // Crear contenido del mensaje
    const textNode = document.createTextNode(text);
    msg.appendChild(textNode);
    
    // Añadir timestamp
    const timeSpan = document.createElement('span');
    timeSpan.className = 'chat-message-time';
    const now = new Date();
    timeSpan.textContent = now.toLocaleTimeString('es-CL', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    msg.appendChild(timeSpan);
    
    // Añadir al contenedor
    chatMessages.appendChild(msg);
    
    // Scroll al final con animación suave
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: 'smooth'
    });
    
    // Limpiar input
    chatInput.value = '';
    
    // Opcional: simular respuesta del otro usuario después de 2 segundos
    setTimeout(() => {
      simulateResponse('Mensaje recibido ');
    }, 2000);
  }

  // ========================================
  // SIMULAR RESPUESTA (Para testing)
  // ========================================
  function simulateResponse(text) {
    if (!chatMessages) return;
    
    // Mostrar indicador de escritura
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(typingIndicator);
    
    // Scroll al indicador
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: 'smooth'
    });
    
    // Después de 1 segundo, mostrar mensaje
    setTimeout(() => {
      // Remover indicador
      typingIndicator.remove();
      
      // Crear mensaje recibido
      const msg = document.createElement('div');
      msg.className = 'chat-message received'; 
      
      const textNode = document.createTextNode(text);
      msg.appendChild(textNode);
      
      // Timestamp
      const timeSpan = document.createElement('span');
      timeSpan.className = 'chat-message-time';
      const now = new Date();
      timeSpan.textContent = now.toLocaleTimeString('es-CL', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      msg.appendChild(timeSpan);
      
      chatMessages.appendChild(msg);
      
      // Scroll al final
      chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
      });
    }, 1000);
  }

  // ========================================
  // EVENT LISTENERS PARA ENVIAR
  // ========================================
  if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
  }

  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevenir salto de línea
        sendMessage();
      }
    });
  }

  // ========================================
  // CERRAR PANEL AL HACER CLICK FUERA
  // ========================================
  document.addEventListener('click', (e) => {
    const isClickInsidePanel = panel.contains(e.target);
    const isClickOnButton = btn.contains(e.target);
    const isPanelOpen = panel.getAttribute('aria-hidden') === 'false';
    
    if (!isClickInsidePanel && !isClickOnButton && isPanelOpen) {
      panel.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-label', 'Abrir chat');
    }
  });
});