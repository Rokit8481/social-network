(() => {
    'use strict';

    const WS_URL = (() => {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        return `${protocol}://${window.location.host}/ws/notifications/`;
    })();

    let socket = null;
    let reconnectTimeout = null;
    let loadedOld = false;

    function getContainer() {
        return document.getElementById('notifications-container');
    }

    async function loadOldNotifications() {
        if (loadedOld) return;

        const res = await fetch('/notifications/api/');
        const data = await res.json();

        const container = getContainer();
        container.innerHTML = '';

        data.forEach(n => renderNotification(n, true));
        loadedOld = true;
    }

    function renderNotification(notification, fromHistory = false) {
        const container = getContainer();
        const badge = document.getElementById('notifications-badge');

        const el = document.createElement('div');
        el.className = `
            d-flex justify-content-between align-items-start
            px-3 py-2 border-bottom notification-item
        `;

        el.innerHTML = `
            <div class="me-2 flex-grow-1">
                <div class="small">${notification.message}</div>
                <div class="text-light notification-time">${notification.created || 'just now'}</div>
            </div>

            ${notification.is_read ? '' : `
                <button class="mark-read-btn" title="Позначити прочитаним">✓</button>
            `}
        `;

        if (!notification.is_read) {
            const btn = el.querySelector('.mark-read-btn');

            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                e.preventDefault();

                await fetch(`/notifications/api/${notification.id}/read/`);

                el.classList.add('bg-dark');
                btn.remove();
            });
        }

        if (fromHistory) {
            container.appendChild(el);
        } else {
            container.prepend(el);

            badge.classList.remove('d-none');
            badge.textContent = parseInt(badge.textContent || 0) + 1;
        }
    }


    function connect() {
        socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            console.log('[Notifications] connected');
        };

        socket.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                renderNotification(data);
            } catch {
                console.error('[Notifications] invalid JSON');
            }
        };

        socket.onclose = () => {
            reconnect();
        };

        socket.onerror = () => {
            socket.close();
        };
    }

    function reconnect() {
        if (reconnectTimeout) return;
        reconnectTimeout = setTimeout(() => {
            reconnectTimeout = null;
            connect();
        }, 3000);
    }

    document.addEventListener('DOMContentLoaded', () => {
        connect();

        const toggle = document.getElementById('notificationsToggle');
        const dropdown = document.getElementById('notifications-dropdown');
        const badge = document.getElementById('notifications-badge');

        toggle.addEventListener('click', async (e) => {
            e.stopPropagation();
            e.preventDefault();
            dropdown.classList.toggle('d-none');

            if (!loadedOld) {
                await loadOldNotifications();
            }

            badge.textContent = 0;
            badge.classList.add('d-none');
        });

        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('d-none');
            }
        });
    });
})();