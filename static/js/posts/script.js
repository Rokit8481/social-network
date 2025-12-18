document.addEventListener("DOMContentLoaded", () => {

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const postId = btn.dataset.postId;
            const likesCountSpan = btn.querySelector(".likes-count");

            fetch(`/posts/api/post/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                likesCountSpan.textContent = data.likes_count;
            });
        });
    });

    document.querySelectorAll(".like-comment-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const commentId = btn.dataset.commentId;
            const likesCountSpan = btn.querySelector(".comment-likes-count");

            fetch(`/posts/api/comment/like/${commentId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                likesCountSpan.textContent = data.likes_count;
            });
        });
    });

    const commentForm = document.getElementById("comment-form");
    if (!commentForm) return;

    const textarea = commentForm.querySelector("textarea");
    const submitBtn = commentForm.querySelector("button[type='submit']");

    let editingCommentId = null;

    document.querySelectorAll(".comment-update-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            e.preventDefault();

            editingCommentId = btn.dataset.messageId;
            const commentDiv = document.querySelector(`[data-comment-id="${editingCommentId}"]`);
            const textElement = commentDiv.querySelector(".comment-text");

            textarea.value = textElement.textContent.trim();
            textarea.focus();

            submitBtn.style.display = "none";
            addEditButtons();
        });
    });

    function addEditButtons() {
        if (document.getElementById("save-edit-btn")) return;

        const saveBtn = document.createElement("button");
        saveBtn.id = "save-edit-btn";
        saveBtn.className = "btn btn-success w-100 mb-2";
        saveBtn.textContent = "💾 Save";

        const cancelBtn = document.createElement("button");
        cancelBtn.id = "cancel-edit-btn";
        cancelBtn.className = "btn btn-secondary w-100";
        cancelBtn.textContent = "✖ Cancel";

        commentForm.append(saveBtn, cancelBtn);

        saveBtn.addEventListener("click", saveEdit);
        cancelBtn.addEventListener("click", cancelEdit);
    }

    async function saveEdit(e) {
        e.preventDefault();

        const newContent = textarea.value.trim();
        if (!newContent) {
            alert("Порожній коментар");
            return;
        }

        const res = await fetch(`/posts/comment/${editingCommentId}/edit/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: newContent })
        });

        const data = await res.json();
        if (!data.success) return alert(data.error || "Error");

        document
            .querySelector(`[data-comment-id="${editingCommentId}"] .comment-text`)
            .textContent = data.comment.content;

        finishEditing();
    }

    function cancelEdit(e) {
        e.preventDefault();
        finishEditing();
    }

    function finishEditing() {
        editingCommentId = null;
        textarea.value = "";
        submitBtn.style.display = "block";

        document.getElementById("save-edit-btn")?.remove();
        document.getElementById("cancel-edit-btn")?.remove();
    }

    document.querySelectorAll(".media-item").forEach(item => {
        item.addEventListener("click", () => {
            const index = item.dataset.index;
            const carousel = document.querySelector(
                item.dataset.bsTarget + " .carousel"
            );
            bootstrap.Carousel.getOrCreateInstance(carousel).to(index);
        });
    });

});

document.querySelectorAll("[data-copy-comment]").forEach(btn => {
    btn.addEventListener("click", () => {
        const commentId = btn.dataset.copyComment;
        const commentText = document
            .querySelector(`[data-comment-id="${commentId}"] .comment-text`)
            .textContent;

        navigator.clipboard.writeText(commentText);
    });
});