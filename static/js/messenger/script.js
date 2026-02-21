// Перемикання між списками чатів та користувачів
document.getElementById('btn-users')?.addEventListener('click', () => {
    document.getElementById('user-list')?.classList.remove('d-none');
    document.getElementById('chat-list')?.classList.add('d-none');
    document.getElementById('btn-users')?.classList.replace('btn-outline-primary', 'btn-primary');
    document.getElementById('btn-chats')?.classList.replace('btn-primary', 'btn-outline-secondary');
});

document.getElementById('btn-chats')?.addEventListener('click', () => {
    document.getElementById('chat-list')?.classList.remove('d-none');
    document.getElementById('user-list')?.classList.add('d-none');
    document.getElementById('btn-chats')?.classList.replace('btn-outline-secondary', 'btn-primary');
    document.getElementById('btn-users')?.classList.replace('btn-primary', 'btn-outline-primary');
});

// ──────────────────────────────────────────────
// Основні елементи
// ──────────────────────────────────────────────
const chatBox = document.querySelector('#chat-box');
if (!chatBox) console.warn("chat-box not found");

const chatId = chatBox?.dataset.chatId || null;
const form = document.querySelector('#message-form');
const textInput = form?.querySelector('input[name="text"]');
const currentUser = chatBox?.dataset.currentUser || null;

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const socketUrl = `${protocol}://${window.location.host}/ws/chat/${chatId}/`;
const socket = chatId ? new WebSocket(socketUrl) : null;

let currentReplyToId = null;
let editingMessageId = null;

const replyingToContainer = document.getElementById('replying-to');
const replyUserEl = document.getElementById('reply-user');
const replyTextEl = document.getElementById('reply-text');
const cancelReplyBtn = document.getElementById('cancel-reply-btn');
const sendBtn = form?.querySelector('button[type="submit"]');

// ──────────────────────────────────────────────
// Функції для блоку "Відповідаєте на"
// ──────────────────────────────────────────────
function showReplyingTo(user, text, id) {
    if (!replyingToContainer) return;
    replyUserEl.textContent = user || '';
    replyTextEl.textContent = text ? (text.length > 60 ? text.substring(0, 57) + '…' : text) : '';
    replyingToContainer.classList.remove('d-none');
    currentReplyToId = id;
}

function hideReplyingTo() {
    if (replyingToContainer) replyingToContainer.classList.add('d-none');
    currentReplyToId = null;
}

if (cancelReplyBtn) {
    cancelReplyBtn.addEventListener('click', () => {
        hideReplyingTo();
        textInput?.focus();
    });
}

// ──────────────────────────────────────────────
// Реакції
// ──────────────────────────────────────────────
function createReactionButton(emoji, count, users, reactedByMe) {
    const btn = document.createElement('button');
    btn.className = reactedByMe ? 'reaction-btn active-reaction-btn' : 'reaction-btn reaction-inactive-btn';
    btn.dataset.emoji = emoji;

    let html = emoji;
    if (count <= 3) {
        users.forEach((u, i) => {
            html += `<img src="${u.avatar}" alt="${u.username}" class="reaction-avatar"${i > 0 ? ' style="margin-left:-10px;"' : ''}>`;
        });
    } else {
        html += `<span class="reaction-count">${count}</span>`;
    }
    btn.innerHTML = html;

    btn.addEventListener('click', () => {
        const messageId = btn.closest('.message-content')?.dataset.messageId;
        if (messageId) {
            socket?.send(JSON.stringify({
                type: 'reaction_update',
                message_id: messageId,
                emoji
            }));
        }
    });

    return btn;
}

// ──────────────────────────────────────────────
// Обробка повідомлень від WebSocket
// ──────────────────────────────────────────────
if (socket) {
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        switch (data.type) {
            case 'chat_message':
                addMessageToDOM(data);
                break;

            case 'reaction_update':
                const msgEl = document.querySelector(`[data-message-id="${data.message_id}"]`);
                if (!msgEl) return;
                const list = msgEl.querySelector('.reactions-list');
                if (!list) return;
                list.innerHTML = '';
                (data.reactions || []).forEach(r => {
                    const reactedByMe = r.users?.some(u => u.username === currentUser) || false;
                    list.appendChild(createReactionButton(r.emoji, r.count, r.users || [], reactedByMe));
                });
                break;

            case 'message_deleted':
                document.querySelector(`#message-${data.message_id}`)?.remove();
                break;

            case 'update_message':
                const el = document.querySelector(`[data-message-id="${data.id}"]`);
                if (el) {
                    el.querySelector('.message-text')?.replaceChildren(data.text || '');
                    el.classList.remove('editing');
                }
                break;
        }
    };
}

// ──────────────────────────────────────────────
// Обробка кліків
// ──────────────────────────────────────────────
document.addEventListener('click', (e) => {
    const target = e.target;

    // Видалення повідомлення
    if (target.closest('.message-delete-btn')) {
        e.preventDefault();
        if (!confirm('Видалити це повідомлення?')) return;
        const messageId = target.closest('.message-delete-btn')?.dataset.messageId;
        if (messageId) {
            socket?.send(JSON.stringify({ type: 'delete_message', message_id: messageId }));
        }
        return;
    }

    // Редагування повідомлення
    if (target.closest('.message-update-btn')) {
        e.preventDefault();
        const content = target.closest('.message-content');
        if (!content) return;

        const messageId = content.dataset.messageId;
        const text = content.querySelector('.message-text')?.innerText.trim() || '';

        document.querySelectorAll('.message-content.editing').forEach(el => el.classList.remove('editing'));
        content.classList.add('editing');

        textInput.value = text;
        textInput?.focus();

        editingMessageId = messageId;
        sendBtn.textContent = 'Зберегти';
        sendBtn.classList.replace('btn-primary', 'btn-warning');

        hideReplyingTo();
        return;
    }

    // Кнопка "Відповісти" — ЗБОКУ
    if (target.closest('.reply-btn-external')) {
        e.preventDefault();

        const row = target.closest('.message-row');
        const content = row?.querySelector('.message-content');
        if (!content) return;

        if (editingMessageId) {
            textInput.value = '';
            editingMessageId = null;
            sendBtn.textContent = 'Send';
            sendBtn.classList.replace('btn-warning', 'btn-primary');
            document.querySelectorAll('.message-content.editing').forEach(el => el.classList.remove('editing'));
        }

        const replyId = content.dataset.messageId;
        const username = content.querySelector('.message-username')?.textContent.trim();
        let replyText = content.querySelector('.message-text')?.textContent.trim() || '';
        replyText = replyText.length > 80 ? replyText.substring(0, 77) + '…' : replyText;

        showReplyingTo(username, replyText, replyId);
        textInput?.focus();
        return;
    }

    // Клік по reply-indicator → скрол
    if (target.closest('.reply-indicator')) {
        const replyToId = target.closest('.reply-indicator').dataset.replyTo;
        if (replyToId) {
            const targetMsg = document.getElementById(`message-${replyToId}`);
            if (targetMsg) {
                targetMsg.scrollIntoView({ behavior: 'smooth', block: 'center' });
                targetMsg.classList.add('highlighted');
                setTimeout(() => targetMsg.classList.remove('highlighted'), 4000);
            }
        }
    }
});

// ──────────────────────────────────────────────
// Відправка / збереження
// ──────────────────────────────────────────────
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = textInput?.value.trim();
        if (!text) return;

        if (editingMessageId) {
            socket?.send(JSON.stringify({
                type: 'update_message',
                message_id: editingMessageId,
                text
            }));

            textInput.value = '';
            editingMessageId = null;
            sendBtn.textContent = 'Send';
            sendBtn.classList.replace('btn-warning', 'btn-primary');
            hideReplyingTo();
            document.querySelectorAll('.message-content.editing').forEach(el => el.classList.remove('editing'));
        } else {
            const payload = { type: 'chat_message', text };
            if (currentReplyToId) payload.reply_on = currentReplyToId;

            socket?.send(JSON.stringify(payload));
            textInput.value = '';
            hideReplyingTo();
        }
    });
}

// ──────────────────────────────────────────────
// Допоміжні функції
// ──────────────────────────────────────────────
function scrollToBottom() {
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
}

function formatHumanDate(isoDate) {
    const d = new Date(isoDate);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);

    if (d.toDateString() === today.toDateString()) return 'Сьогодні';
    if (d.toDateString() === yesterday.toDateString()) return 'Вчора';

    return d.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' });
}

function createDateDivider(dateISO) {
    const tpl = document.getElementById('date-divider-template');
    if (!tpl) return null;

    const clone = tpl.content.cloneNode(true);
    const divider = clone.querySelector('.chat-date-divider');
    const label = clone.querySelector('span');

    if (divider && label) {
        divider.dataset.date = dateISO;
        label.textContent = formatHumanDate(dateISO);
    }

    return clone;
}

function maybeInsertDateDivider(messageDate) {
    if (!chatBox) return;
    const dividers = chatBox.querySelectorAll('.chat-date-divider');
    const last = dividers[dividers.length - 1];

    if (!last || last.dataset.date !== messageDate) {
        const divider = createDateDivider(messageDate);
        if (divider) chatBox.appendChild(divider);
    }
}

function addMessageToDOM(data) {
    if (!chatBox) return;

    maybeInsertDateDivider(data.created_date);

    const template = document.getElementById('message-template');
    if (!template) return;

    const clone = template.content.cloneNode(true);
    const row = clone.querySelector('.message-row');
    const content = clone.querySelector('.message-content');
    const avatarLink = clone.querySelector('.message-avatar-link');
    const avatarImg = clone.querySelector('.message-avatar');
    const usernameLink = clone.querySelector('.message-username');
    const ownReplyBtn   = clone.querySelector('.reply-btn-external-own');
    const otherReplyBtn = clone.querySelector('.reply-btn-external-other');

    const isOwn = data.user === currentUser;

    if (isOwn) {
        ownReplyBtn?.classList.remove('d-none');
        otherReplyBtn?.classList.add('d-none');
    } else {
        ownReplyBtn?.classList.add('d-none');
        otherReplyBtn?.classList.remove('d-none');
    }


    // Вирівнювання рядка
    row.classList.add(isOwn ? 'justify-content-end' : 'justify-content-start');

    content.classList.add(isOwn ? 'message-own' : 'message-other');
    content.dataset.messageId = data.id;
    if (data.reply_on_id) content.dataset.replyOnId = data.reply_on_id;

    usernameLink.textContent = data.user;
    usernameLink.href = `/users/${data.user_slug}/`;

    if (!isOwn) {
        if (data.avatar) {
            avatarImg.src = data.avatar;
            avatarLink.href = `/users/${data.user_slug}/`;
        }
        avatarLink.classList.remove('d-none');
    }

    clone.querySelector('.message-text').textContent = data.text || '';
    clone.querySelector('.message-time').textContent = data.created_time || '';

    // Дії (edit/delete) тільки для своїх
    if (isOwn) {
        const actions = clone.querySelector('.message-actions');
        if (actions) {
            actions.classList.remove('d-none');
            actions.querySelector('.message-delete-btn').dataset.messageId = data.id;
            actions.querySelector('.message-update-btn').dataset.messageId = data.id;
        }
    }

    // Reply indicator
    if (data.reply_on_id) {
        const replyDiv = document.createElement('div');
        replyDiv.className = 'reply-indicator mb-1 p-1 bg-dark rounded small';
        replyDiv.dataset.replyTo = data.reply_on_id;
        replyDiv.innerHTML = `↩️ Replying to: <span class="reply-user text-primary">${data.reply_on_user || '…'}</span> <span class="reply-text text-light opacity-75">${data.reply_on_text || ''}</span>`;
        content.insertBefore(replyDiv, clone.querySelector('.message-text'));
    }

    // Кнопка "Відповісти" — ЗБОКУ
    const replyBtn = clone.querySelector('.reply-btn-external');
    if (replyBtn) {
        // Завжди показуємо кнопку (можна додати hover логіку в css якщо потрібно)
        replyBtn.classList.remove('d-none'); // якщо була прихована
    }

    chatBox.appendChild(clone);
    scrollToBottom();
}

// ──────────────────────────────────────────────
// Ініціалізація
// ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    scrollToBottom();

    document.querySelectorAll('.chat-date-divider').forEach(div => {
        const date = div.dataset.date;
        if (date) {
            const label = div.querySelector('span');
            if (label) label.textContent = formatHumanDate(date);
        }
    });

    // Контекстне меню → реакції
    document.addEventListener('contextmenu', e => {
        const content = e.target.closest('.message-content');
        if (!content) return;
        e.preventDefault();

        document.querySelectorAll('.emoji-picker').forEach(p => p.classList.add('d-none'));

        const picker = content.querySelector('.emoji-picker');
        if (picker) {
            picker.classList.remove('d-none');
            picker.style.position = 'fixed';
            picker.style.left = `${e.clientX}px`;
            picker.style.top = `${e.clientY}px`;
        }
    });

    document.addEventListener('click', e => {
        const choice = e.target.closest('.emoji-choice');
        if (!choice) return;

        const picker = choice.closest('.emoji-picker');
        const content = picker?.closest('.message-content');
        if (!content) return;

        socket?.send(JSON.stringify({
            type: 'reaction_update',
            message_id: content.dataset.messageId,
            emoji: choice.dataset.emoji
        }));

        picker.classList.add('d-none');
    });

    document.addEventListener('click', e => {
        if (!e.target.closest('.emoji-picker')) {
            document.querySelectorAll('.emoji-picker').forEach(p => p.classList.add('d-none'));
        }
    });

    const bgBox = document.querySelector('.chat-box--bg');
    if (bgBox?.dataset.bgUrl) {
        bgBox.style.backgroundImage = `url(${bgBox.dataset.bgUrl})`;
    }
});