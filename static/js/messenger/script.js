document.getElementById('btn-users').addEventListener('click', function() {
  document.getElementById('user-list').classList.remove('d-none');
  document.getElementById('chat-list').classList.add('d-none');

  this.classList.replace('btn-outline-primary', 'btn-primary');      
  document.getElementById('btn-chats').classList.replace('btn-primary', 'btn-outline-secondary'); 
});

document.getElementById('btn-chats').addEventListener('click', function() {
  document.getElementById('chat-list').classList.remove('d-none');
  document.getElementById('user-list').classList.add('d-none');

  this.classList.replace('btn-outline-secondary', 'btn-primary');     
  document.getElementById('btn-users').classList.replace('btn-primary', 'btn-outline-primary'); 
});

const chatBox = document.querySelector('#chat-box');
const chatId = chatBox.dataset.chatId || null;
const form = document.querySelector('#message-form');
const textInput = form.querySelector('input[name="text"]');
const currentUser = chatBox.dataset.currentUser;

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${chatId}/`);

function createReactionButton(emoji, count, users, userReactedEmojis) {
  const btn = document.createElement('button');
  btn.classList.add('reaction-btn');
  btn.dataset.emoji = emoji;

  if (userReactedEmojis.includes(emoji)) {
      btn.classList.add('active-reaction-btn');
  } else {
      btn.classList.add('reaction-inactive-btn');
  }

  let html = `${emoji} `;

  if (count <= 3) {
      users.forEach((user, index) => {
          const margin = index === 0 ? '' : 'style="margin-left: -8px;"';
          html += `<img src="${user.avatar}" alt="${user.username}" class="reaction-avatar" ${margin} />`;
      });
  } else {
      html += `<span class="reaction-count">${count}</span>`;
  }

  btn.innerHTML = html;

  // Клік на реакцію
  btn.addEventListener('click', () => {
      const messageId = btn.closest('.message-content').dataset.messageId;
      socket.send(JSON.stringify({
          type: 'reaction_update',
          message_id: messageId,
          emoji: emoji
      }));
  });

  const tooltip = document.createElement('div');
  const end_text = document.createElement('div');

  users.forEach(u => {
      const div = document.createElement('div');
      div.classList.add('reaction-user');
      div.innerHTML = `<img src="${u.avatar}" class="avatar-small" alt="${u.username}"><span>${u.username}</span>`;
      tooltip.appendChild(div);
  });
  
  if (users.length > 3) {
      const end_text = document.createElement('div');
      end_text.textContent = `+${users.length - 3} others`;
      end_text.classList.add(
          'reaction-user',
          'mt-1',
          'text-center',
          'text-light',
          'fw-bold'
      );
      tooltip.appendChild(end_text);
  }
  tooltip.classList.add('reaction-tooltip', 'd-none');
  document.body.appendChild(tooltip);

  btn.addEventListener('mouseenter', () => {
      const rect = btn.getBoundingClientRect();
      tooltip.style.position = 'fixed';
      tooltip.style.top = `${rect.bottom + 5}px`;
      tooltip.style.left = `${rect.left}px`;
      tooltip.classList.remove('d-none');
  });

  // Ховати тултіп тільки при кліку поза ним і кнопкою
  document.addEventListener('click', e => {
      if (!tooltip.contains(e.target) && e.target !== btn) {
          tooltip.classList.add('d-none');
      }
  });

  return btn;
}

function attachReactionTooltips() {
  document.querySelectorAll('.reaction-btn').forEach(btn => {
    const tooltip = btn.querySelector('.reaction-tooltip');
    if (!tooltip) return;

    btn.addEventListener('mouseenter', () => {
        const rect = btn.getBoundingClientRect();
        tooltip.style.top = `${rect.bottom + window.scrollY}px`;
        tooltip.style.left = `${rect.left + window.scrollX}px`;
        tooltip.classList.remove('d-none');
    });
    btn.addEventListener('mouseleave', () => {
      tooltip.classList.add('d-none');
    });
  });
}


socket.onmessage = function(e) {
  const data = JSON.parse(e.data);

  if (data.type === 'chat_message') {
    addMessageToDOM(data);
  }

  if (data.type === 'reaction_update') {
    const msgEl = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (!msgEl) return;

    const list = msgEl.querySelector('.reactions-list');
    list.innerHTML = '';

    data.counts.forEach(r => {
      const btn = createReactionButton(r.emoji, r.count, r.users, data.user_reacted_emojis);
      list.appendChild(btn);
    });
  }
  if (data.type === 'message_deleted') {
    const msg = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (msg) msg.remove();
  }
  if (data.type === 'update_message') { 
    const msgEl = document.querySelector(`[data-message-id="${data.id}"]`);
    if (msgEl) {
      const messageTextEl = msgEl.querySelector('.message-text');
      if (messageTextEl) {
        messageTextEl.innerText = data.text;
        msgEl.classList.remove('editing');
      }
    }
  }    
};

const deleteChatBtn = document.getElementById('chat-delete-btn');
if (deleteChatBtn && chatId) {
  const deleteChatUrl = deleteChatBtn.dataset.deleteUrl;

  deleteChatBtn.addEventListener('click', function(e) {
    e.preventDefault();
    const confirmed = confirm("Ви впевнені що хочете видалити цей чат?");
    if (!confirmed) return;

    fetch(deleteChatUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": CSRF_TOKEN,
        "Accept": "application/json",
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = data.redirect_url;
      }
    })
    .catch(err => console.error(err));
  });
}

document.querySelectorAll('.message-delete-btn').forEach(btn => {
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    if (!confirm("Ви впевнені що хочете видалити це повідомлення?")) return;

    const messageId = this.dataset.messageId;

    socket.send(JSON.stringify({
      type: "delete_message",
      message_id: messageId
    }));
  });
});


let editingMessageId = null;
const sendBtn = form.querySelector('button[type="submit"]');

document.querySelectorAll(".message-update-btn").forEach(btn => {
  btn.addEventListener("click", function (e) {
    e.preventDefault();
    const messageBlock = this.closest('.message-content');
    const messageId = this.dataset.messageId;
    const messageTextEl = messageBlock.querySelector('.message-text');
    const messageText = messageTextEl ? messageTextEl.innerText.trim() : '';

    document.querySelectorAll('.message-content').forEach(el => el.classList.remove('editing'));
    messageBlock.classList.add('editing');


    textInput.value = messageText;
    textInput.focus();

    editingMessageId = messageId;
    sendBtn.textContent = "Зберегти зміни";
    sendBtn.classList.remove("btn-primary");
    sendBtn.classList.add("btn-warning");
  });
});

form.addEventListener('submit', e => {
  e.preventDefault();
  const text = textInput.value.trim();
  if (!text) return;

  if (editingMessageId) {
    socket.send(JSON.stringify({
      type: "update_message",
      message_id: editingMessageId,
      text: text
    }));
  
    textInput.value = "";
    editingMessageId = null;
    sendBtn.textContent = "Надіслати";
    sendBtn.classList.remove("btn-warning");
    sendBtn.classList.add("btn-primary");
  }
  else {
    socket.send(JSON.stringify({
      type: 'chat_message',
      text: text
    }));
    textInput.value = '';
  }    
});  

function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

function attachRightClickEvents() {
  document.querySelectorAll('.message-content').forEach(msg => {
    msg.oncontextmenu = e => {
      e.preventDefault();
      document.querySelectorAll('.emoji-picker').forEach(p => p.classList.add('d-none'));
      const picker = msg.querySelector('.emoji-picker');
      if (!picker) return;
      picker.style.position = 'fixed'; 
      picker.style.top = e.clientY + 'px';
      picker.style.left = e.clientX + 'px';
      picker.classList.remove('d-none');
    };
  });
}

function attachEmojiClickEvents() {
  document.querySelectorAll('.emoji-choice').forEach(choice => {
    choice.onclick = () => {
      const emoji = choice.dataset.emoji;
      const picker = choice.closest('.emoji-picker');
      const messageId = picker.closest('.message-content').dataset.messageId;

      socket.send(JSON.stringify({
        type: 'reaction_update',
        message_id: messageId,
        emoji: emoji
      }));

      picker.classList.add('d-none');
    };
  });
}

document.addEventListener('click', e => {
  if (!e.target.closest('.emoji-picker')) {
    document.querySelectorAll('.emoji-picker').forEach(p => p.classList.add('d-none'));
  }
});

const chatBoxBg = document.querySelector('.chat-box--bg');
if (chatBoxBg) {
  chatBoxBg.style.backgroundImage = `url(${chatBoxBg.dataset.bgUrl})`;
}

function addMessageToDOM(data) {
  const template = document.getElementById('message-template');
  if (!template) return;

  const clone = template.content.cloneNode(true);

  const row = clone.querySelector('.message-row');
  const content = clone.querySelector('.message-content');
  const avatarLink = clone.querySelector('.message-avatar-link');
  const avatarImg = clone.querySelector('.message-avatar');
  const usernameLink = clone.querySelector('.message-username');

  const isOwn = data.user === currentUser;

  row.classList.add(isOwn ? 'justify-content-end' : 'justify-content-start');
  content.classList.add(isOwn ? 'message-own' : 'message-other');

  content.dataset.messageId = data.id;

  // username + link
  usernameLink.textContent = data.user;
  usernameLink.href = `/users/${data.user_slug}/`;

  // avatar
  if (!isOwn) {
    avatarImg.src = data.avatar;
    avatarLink.href = `/users/${data.user_slug}/`;
    avatarLink.classList.remove('d-none');
  }

  // text + time
  clone.querySelector('.message-text').textContent = data.text;
  clone.querySelector('.message-time').textContent = data.created_time;

  // actions (тільки свої)
  if (isOwn) {
    const actions = clone.querySelector('.message-actions');
    actions.classList.remove('d-none');

    actions.querySelector('.message-delete-btn').dataset.messageId = data.id;
    actions.querySelector('.message-update-btn').dataset.messageId = data.id;
  }

  chatBox.appendChild(clone);

  scrollToBottom();
}

document.addEventListener('DOMContentLoaded', () => {
  attachEmojiClickEvents();
  attachRightClickEvents();
  attachReactionTooltips();
});
