// xat/static/xat/js/xat.js
function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function createMessageElement(msg) {
    const div = document.createElement('div');
    div.className = `xat-message${msg.is_highlighted ? ' highlighted' : ''}`;
    div.dataset.messageId = msg.id;

    const header = `<div class="message-header">
        <strong>${escapeHtml(msg.display_name)}</strong>
        <small class="text-muted">${escapeHtml(msg.created_at)}</small>
    </div>`;
    const content = `<div class="message-content">${escapeHtml(msg.message)}</div>`;
    const actions = msg.can_delete ?
        `<div class="message-actions"><button class="btn btn-sm btn-outline-danger delete-message" data-id="${msg.id}">🗑️</button></div>` : '';

    div.innerHTML = header + content + actions;
    return div;
}

function scrollToBottom() {
    const container = document.getElementById('xat-messages');
    container.scrollTop = container.scrollHeight;
}

function updateMessageCount(count) {
    document.getElementById('message-count').textContent = count;
}

async function loadMessages() {
    try {
        const res = await fetch(`/xat/${eventId}/messages/`);
        const data = await res.json();
        const container = document.getElementById('xat-messages');
        container.innerHTML = '';
        data.messages.forEach(msg => container.appendChild(createMessageElement(msg)));
        scrollToBottom();
        updateMessageCount(data.messages.length);
    } catch (e) { console.error(e); }
}

async function sendMessage(e) {
    e.preventDefault();
    const form = e.target;
    const textarea = form.querySelector('textarea');
    const msg = textarea.value.trim();
    const token = form.querySelector('[name=csrfmiddlewaretoken]').value;
    if (!msg) return;

    try {
        const res = await fetch(`/xat/${eventId}/send/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': token },
            body: `message=${encodeURIComponent(msg)}`
        });
        const result = await res.json();
        if (result.success) {
            textarea.value = '';
            document.getElementById('xat-errors').textContent = '';
            loadMessages();
        } else {
            document.getElementById('xat-errors').textContent = Object.values(result.errors).flat().join(' ');
        }
    } catch (e) { console.error(e); }
}

async function deleteMessage(id) {
    if (!confirm('Segur que vols eliminar?')) return;
    const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    try {
        await fetch(`/xat/message/${id}/delete/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': token }
        });
        loadMessages();
    } catch (e) { console.error(e); }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('xat-form');
    if (form) form.addEventListener('submit', sendMessage);

    document.getElementById('xat-messages').addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-message')) {
            deleteMessage(e.target.dataset.id);
        }
    });

    loadMessages();
    setInterval(loadMessages, 3000); // polling cada 3s
});