document.addEventListener("DOMContentLoaded", () => {
    initTagsToggle();
    initMessageForm();
    initMessageActions();
});

/* ===================== TAGS ===================== */
function initTagsToggle() {
    const TAGS_TO_SHOW = 3;

    document.querySelectorAll('.tags-container').forEach(container => {
        const tags = Array.from(container.querySelectorAll('.tag-item'));
        const showBtn = container.querySelector('.show-more-tags');
        const hideBtn = container.querySelector('.hide-tags');

        if (!showBtn || !hideBtn || tags.length <= TAGS_TO_SHOW) return;

        let visibleCount = TAGS_TO_SHOW;

        tags.forEach((tag, i) => {
            tag.style.display = i < TAGS_TO_SHOW ? 'inline-block' : 'none';
        });

        showBtn.addEventListener('click', () => {
            visibleCount += TAGS_TO_SHOW;

            tags.forEach((tag, i) => {
                if (i < visibleCount) {
                    tag.style.display = 'inline-block';
                }
            });
            hideBtn.style.display = 'inline-block';

            if (visibleCount >= tags.length) {
                showBtn.style.display = 'none';
            }
        });

        hideBtn.addEventListener('click', () => {
            visibleCount = TAGS_TO_SHOW;

            tags.forEach((tag, i) => {
                tag.style.display = i < TAGS_TO_SHOW ? 'inline-block' : 'none';
            });

            hideBtn.style.display = 'none';
            showBtn.style.display = 'inline-block';
        });
    });
}

/* ===================== MESSAGE FORM (CREATE / EDIT) ===================== */

function initMessageForm() {
    const form = document.getElementById('new-message-form');
    const container = document.querySelector('.board-messages');
    if (!form || !container) return;

    const textarea = document.getElementById("message-input");
    const editInput = document.getElementById("edit-message-id");
    const sendBtn = document.getElementById("send-btn");
    const cancelBtn = document.getElementById("cancel-edit-btn");
    const errorsDiv = document.getElementById("message-errors");

    const resetEditMode = () => {
        editInput.value = "";
        textarea.value = "";
        sendBtn.textContent = "Send";
        cancelBtn.classList.add("d-none");
    };

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const content = textarea.value.trim();
        const editId = editInput.value;
        if (!content) return;

        let url = container.dataset.createUrl;
        if (editId) url = container.dataset.editUrl.replace("0", editId);

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: new URLSearchParams({ content })
        })
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            if (!data.success) {
                errorsDiv.textContent = JSON.stringify(data.errors || data);
                return;
            }

            if (editId) {
                const msgDiv = document.querySelector(`.board-message-item[data-id="${editId}"]`);
                if (msgDiv) {
                    msgDiv.querySelector(".board-message-content").textContent = data.content;
                }
            } else {
                addMessageToDOM(data);
            }

            resetEditMode();
            errorsDiv.textContent = "";
        })
        .catch((err) => {
            console.error("Network error:", err);
            errorsDiv.textContent = "Network error";
        });
    });

    cancelBtn.addEventListener("click", () => {
        resetEditMode();
    });
}

/* ===================== MESSAGE ACTIONS ===================== */
function initMessageActions() {
    const container = document.querySelector('.board-messages');
    if (!container) return;

    const DELETE_URL_TEMPLATE = container.dataset.deleteUrl;
    const textarea = document.getElementById("message-input");
    const editInput = document.getElementById("edit-message-id");
    const sendBtn = document.getElementById("send-btn");
    const cancelBtn = document.getElementById("cancel-edit-btn");

    const handleEditMessage = (msgDiv) => {
        const text = msgDiv.querySelector('.board-message-content')?.textContent.trim() || "";
        const msgId = msgDiv.dataset.id;

        textarea.value = text;
        textarea.focus();
        editInput.value = msgId;
        sendBtn.textContent = "Save";
        cancelBtn.classList.remove("d-none");

        textarea.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    const handleDeleteMessage = (msgDiv, msgId) => {
        if (!confirm('Are you sure you want to delete this message?')) return;
        const url = DELETE_URL_TEMPLATE.replace("0", msgId);

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) msgDiv.remove();
            else alert("Failed to delete message");
        })
        .catch(() => alert("Network error"));
    };

    const handleCopyMessage = (msgDiv) => {
        const text = msgDiv.querySelector('.board-message-content')?.innerText.trim();
        if (text) navigator.clipboard?.writeText(text);
    };

    container.addEventListener("click", (e) => {
        const msgDiv = e.target.closest(".board-message-item");
        if (!msgDiv) return;

        const msgId = msgDiv.dataset.id;

        if (e.target.closest(".edit-message-btn")) handleEditMessage(msgDiv);
        else if (e.target.closest(".delete-message-btn")) handleDeleteMessage(msgDiv, msgId);
        else if (e.target.closest("[data-copy-message]")) handleCopyMessage(msgDiv);
    });

    document.querySelectorAll(".media-item-small").forEach(item => {
        item.addEventListener("click", () => {
            const carousel = document.querySelector(item.dataset.bsTarget + " .carousel");
            bootstrap.Carousel.getOrCreateInstance(carousel).to(item.dataset.index);
        });
    });
}

/* ===================== ADD MESSAGE TO DOM ===================== */
function addMessageToDOM(data) {
    const container = document.querySelector(".board-messages");
    const template = document.getElementById("message-template");
    const endText = document.querySelector(".end-text")
    if (!template) return;

    const clone = template.content.cloneNode(true);
    const msgDiv = clone.querySelector(".board-message-item");

    msgDiv.dataset.id = data.id;
    const avatar = clone.querySelector(".msg-avatar");
    avatar.src = data.sender_avatar_url; 
    clone.querySelector(".msg-sender").textContent = data.sender;
    clone.querySelector(".msg-created").textContent = data.created_at;
    clone.querySelector(".board-message-content").textContent = data.content;

    container.insertBefore(clone, container.firstChild);
    endText?.classList.add("d-none")
    container.scrollTop = 0;
}
