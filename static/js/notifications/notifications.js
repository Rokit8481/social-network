
(() => {
    'use strict';

    const WS_URL = (() => {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        return `${protocol}://${window.location.host}/ws/notifications/`;
    })();

    let socket = null;
    let reconnectTimeout = null;

    function connect() {
        socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            console.log('[Notifications] connected');
        };

        socket.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                renderNotification(data);
            } catch (err) {
                console.error('[Notifications] invalid JSON', err);
            }
        };

        socket.onclose = () => {
            console.warn('[Notifications] disconnected, reconnecting...');
            reconnect();
        };

        socket.onerror = (err) => {
            console.error('[Notifications] socket error', err);
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

    function renderNotification(notification) {
        const container = getContainer();

        const el = document.createElement('div');
        el.className = 'alert alert-info alert-dismissible fade show shadow-sm mb-2';
        el.setAttribute('role', 'alert');
        el.innerHTML = `
            <div class="small">${notification.message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(el);

        setTimeout(() => {
            el.classList.remove('show');
            el.remove();
        }, 5000);
    }

    function getContainer() {
        let container = document.getElementById('notifications-container');
        if (container) return container;

        container = document.createElement('div');
        container.id = 'notifications-container';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            width: 320px;
        `;
        document.body.appendChild(container);
        return container;
    }

    document.addEventListener('DOMContentLoaded', connect);
})();
