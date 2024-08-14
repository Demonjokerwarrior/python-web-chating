// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    function loadMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(data => {
                const messages = data.messages;
                const messagesList = document.getElementById('messages');
                messagesList.innerHTML = '';
                messages.forEach(msg => {
                    const li = document.createElement('li');
                    li.textContent = `${msg.username}: ${msg.message}`;
                    messagesList.appendChild(li);
                });
                messagesList.scrollTop = messagesList.scrollHeight; // Scroll to the bottom
            });
    }

    document.getElementById('message-form').addEventListener('submit', function(event) {
        event.preventDefault();
        let message = document.getElementById('message').value;
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                message: message
            })
        }).then(response => response.json()).then(data => {
            if (data.success) {
                document.getElementById('message').value = '';
                loadMessages();
            }
        });
    });

    // Load messages on page load
    loadMessages();

    // Poll for new messages every 5 seconds
    setInterval(loadMessages, 5000);
});
