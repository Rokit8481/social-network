(() => {
    'use strict';

    const IS_AUTH = document.body.dataset.authenticated === 'true';
    if (!IS_AUTH) return;
    const IS_PAGE = document.body.dataset.notificationsPage === 'true';
    console.log('Notifications page mode:', IS_PAGE);

    const WS_URL = (() => {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        return `${protocol}://${window.location.host}/ws/notifications/`;
    })();

    let socket = null;
    let reconnectTimeout = null;
    let loadedOld = false;

    function getContainer() {
        const container = IS_PAGE
                    ? document.querySelector('.notifications-container')
                    : document.querySelector('#notifications-container');
        if (!container) console.warn('Notifications container not found!');
        return container;
    }

    function toggleMarkAllReadButton() {
        const container = getContainer();
        if (!container) return;

        const hasUnread = container.querySelector('.unread') !== null;
        const buttons = document.querySelectorAll('.mark-all-read-btn');
        buttons.forEach(btn => {
            if (hasUnread) {
                btn.classList.remove('d-none');
            } else {
                btn.classList.add('d-none');
            }
        });
    }

    async function loadOldNotifications() {
        if (loadedOld) return;
        try {
            const url = IS_PAGE
                ? '/notifications/api/'
                : '/notifications/api/unread/';
            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to fetch notifications');
            const data = await res.json();

            const container = getContainer();
            if (!container) return;

            container.innerHTML = '';
            data.forEach(n => renderNotification(n, true));
            loadedOld = true;

            toggleMarkAllReadButton();
        } catch (err) {
            console.error('Error loading old notifications:', err);
        }
    }

    async function loadUnreadCount() {
        if (IS_PAGE) return;
        try {
            const res = await fetch('/notifications/api/unread_count/');
            if (!res.ok) throw new Error('Failed to fetch unread count');
            const data = await res.json();

            const badge = document.getElementById('notifications-badge');
            if (!badge) return;

            if (data.count > 0) {
                badge.textContent = data.count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        } catch (err) {
            console.error('Error loading unread count:', err);
        }
    }

    function updateBadge(count) {
        if (IS_PAGE) return;
        const badge = document.getElementById('notifications-badge');
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }

    async function loadNotifications(page = 1) {
        try {
            const url = `/notifications/api/?page=${page}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to fetch notifications');

            const data = await res.json();
            const container = document.querySelector('.notifications-container');
            if (!container) return;

            container.innerHTML = '';
            data.results.forEach(n => renderNotification(n, true));

            renderPaginator(data.page, data.num_pages);

        } catch (err) {
            console.error('Error loading notifications:', err);
        }
    }

    function renderPaginator(currentPage, totalPages) {
        const container = document.querySelector('.pagination-wrapper');
        if (!container) return;

        let html = '<ul class="custom-pagination">';

        if (currentPage > 1) {
            html += `<li><a href="#" data-page="${currentPage - 1}">‹</a></li>`;
        }

        const maxVisible = 7; 
        let startPage = 1;
        let endPage = totalPages;

        if (totalPages > maxVisible) {
            if (currentPage <= 4) {
                startPage = 1;
                endPage = maxVisible;
            } else if (currentPage >= totalPages - 3) {
                startPage = totalPages - (maxVisible - 1);
                endPage = totalPages;
            } else {
                startPage = currentPage - 3;
                endPage = currentPage + 3;
            }
        }

        if (startPage > 1) {
            html += `<li><a href="#" data-page="1">1</a></li>`;
            html += `<li class="dots">…</li>`;
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="${i === currentPage ? 'active' : ''}">
                        <a href="#" data-page="${i}">${i}</a>
                    </li>`;
        }

        if (endPage < totalPages) {
            html += `<li class="dots">…</li>`;
            html += `<li><a href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }

        if (currentPage < totalPages) {
            html += `<li><a href="#" data-page="${currentPage + 1}">›</a></li>`;
        }

        html += '</ul>';
        container.innerHTML = html;

        container.querySelectorAll('a[data-page]').forEach(a => {
            a.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = parseInt(a.dataset.page);
                await loadNotifications(page);
            });
        });
    }


    function renderNotification(notification, fromHistory = false) {
        const container = getContainer();
        if (!container) return;

        const li = document.createElement(IS_PAGE ? 'li' : 'div');
        li.className = IS_PAGE 
            ? `notification-site-item ${notification.is_read ? '' : 'unread'}`
            : `notification-item ${notification.is_read ? '' : 'unread'}`;

        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1 me-2">
                    <div class="small">${notification.message}</div>
                    <div class="text-light notification-time">${notification.created || 'just now'}</div>
                </div>
                ${notification.is_read ? '' : `<button class="mark-read-btn" title="Mark read">✓</button>`}
            </div>
        `;

        if (!notification.is_read) {
            const btn = li.querySelector('.mark-read-btn');
            btn?.addEventListener('click', async (e) => {
                e.stopPropagation();
                e.preventDefault();
                await fetch(`/notifications/api/${notification.id}/read/`);
                li.classList.remove('unread');
                btn.remove();
                if (!IS_PAGE) await loadUnreadCount();
                toggleMarkAllReadButton();
            });
        }

        if (fromHistory) {
            container.appendChild(li);
        } else {
            container.prepend(li);
        }

        toggleMarkAllReadButton();
    }

    function connect() {
        try {
            socket = new WebSocket(WS_URL);

            socket.onopen = () => console.log('[Notifications] connected');
            socket.onmessage = (e) => {
                const data = JSON.parse(e.data);
                renderNotification(data.notification);
                updateBadge(data.unread_count);
            };
            socket.onclose = () => reconnect();
            socket.onerror = () => socket.close();
        } catch (err) {
            console.error('WebSocket connection failed:', err);
        }
    }

    function reconnect() {
        if (reconnectTimeout) return;
        reconnectTimeout = setTimeout(() => {
            reconnectTimeout = null;
            connect();
        }, 3000);
    }

    document.addEventListener('DOMContentLoaded', async () => {
        connect();

        const toggle = document.getElementById('notificationsToggle');
        const dropdown = document.getElementById('notifications-dropdown');

        if (IS_PAGE) {
            toggle?.classList.add('d-none');
            dropdown?.classList.add('d-none');
            await loadNotifications(1);
        } else {
            await loadUnreadCount();

            toggle?.addEventListener('click', async (e) => {
                e.stopPropagation();
                e.preventDefault();
                dropdown?.classList.toggle('d-none');
                if (!loadedOld) await loadOldNotifications();
            });

            document.addEventListener('click', (e) => {
                if (!toggle?.contains(e.target) && !dropdown?.contains(e.target)) {
                    dropdown?.classList.add('d-none');
                }
            });
        }
    });

    document.addEventListener('click', async (e) => {
        if (e.target.matches('.mark-all-read-btn')) {
            e.preventDefault();
            try {
                const res = await fetch('/notifications/api/mark_all_read/');
                if (!res.ok) throw new Error('Failed to mark all read');
                
                document.querySelectorAll('.unread').forEach(el => {
                    el.classList.remove('unread');
                    const btn = el.querySelector('.mark-read-btn');
                    btn?.remove();
                });

                toggleMarkAllReadButton(); 
                if (!IS_PAGE) await loadUnreadCount(); 
            } catch (err) {
                console.error('Error marking all read:', err);
            }
        }
    });
})();