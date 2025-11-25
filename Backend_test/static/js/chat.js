document.addEventListener('DOMContentLoaded', () => {
    const chatHeader = document.getElementById('chatHeader');
    const chatContainer = document.getElementById('chatContainer');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    // Toggle chat expand/collapse
    chatHeader.addEventListener('click', () => {
        chatContainer.classList.toggle('collapsed');
        chatHeader.classList.toggle('collapsed');
        if(chatContainer.classList.contains('collapsed')){
            chatMessages.style.display='none';
            document.querySelector('.chat-input').style.display='none';
        } else {
            chatMessages.style.display='flex';
            document.querySelector('.chat-input').style.display='flex';
        }
    });

    // Send message
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e){
        if(e.key === 'Enter') sendMessage();
    });

    function sendMessage(){
        const text = chatInput.value.trim();
        if(!text) return;
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message');
        const now = new Date();
        const hours = now.getHours().toString().padStart(2,'0');
        const minutes = now.getMinutes().toString().padStart(2,'0');
        msgDiv.innerHTML = `${text} <span class="time">${hours}:${minutes}</span>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        chatInput.value='';
    }
});
