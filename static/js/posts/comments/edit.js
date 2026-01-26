export function initCommentEdit() {
    const form = document.getElementById("comment-form");
    if (!form) return;

    const textarea = form.querySelector("textarea");
    const submitBtn = form.querySelector("button[type='submit']");
    const editActions = form.querySelector(".edit-actions");
    const commentSubmit = form.querySelector(".comment-sumbmit");

    let editingId = null;

    document.addEventListener("click", e => {
        const editBtn = e.target.closest(".comment-update-btn");
        const cancelBtn = e.target.closest("#cancel-edit-btn");
        const saveBtn = e.target.closest("#save-edit-btn");

        if (editBtn) startEdit(editBtn);
        if (cancelBtn) cancelEdit(e);
        if (saveBtn) saveEdit(e);
    });

    function startEdit(btn) {
        editingId = btn.dataset.messageId;

        const comment = document.querySelector(
            `[data-comment-id="${editingId}"] .comment-text`
        );

        textarea.value = comment.textContent.trim();
        textarea.focus();

        submitBtn.classList.add("d-none");
        commentSubmit.classList.add("d-none");

        if (!document.getElementById("save-edit-btn")) {
            editActions.insertAdjacentHTML(
                "beforeend",
                `
                <button id="save-edit-btn" class="btn btn-success flex-grow-1">💾 Save</button>
                <button id="cancel-edit-btn" class="btn btn-secondary flex-grow-1">✖ Cancel</button>
                `
            );
        }
    }

    async function saveEdit(e) {
        e.preventDefault();
        if (!editingId) return;

        const content = textarea.value.trim();
        if (!content) return alert("Empty comment");

        const res = await fetch(`/posts/comment/${editingId}/edit/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content })
        });

        const data = await res.json();
        if (!data.success) return alert(data.error || "Error");

        document.querySelector(
            `[data-comment-id="${editingId}"] .comment-text`
        ).textContent = data.comment.content;

        finishEdit();
    }

    function cancelEdit(e) {
        e.preventDefault();
        finishEdit();
    }

    function finishEdit() {
        editingId = null;
        textarea.value = "";

        submitBtn.classList.remove("d-none");
        commentSubmit.classList.remove("d-none");

        document.getElementById("save-edit-btn")?.remove();
        document.getElementById("cancel-edit-btn")?.remove();
    }
}
