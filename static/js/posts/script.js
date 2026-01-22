document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const postId = btn.dataset.postId;
            const likesCountSpan = btn.querySelector(".likes-count");

            fetch(`/posts/api/post/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
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
                    "X-CSRFToken": CSRF_TOKEN,
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
        
        const editActionsContainer = document.querySelector(".edit-actions")
        const commentSubmit = document.querySelector(".comment-sumbmit")
        const saveBtn = document.createElement("button");
        saveBtn.id = "save-edit-btn";
        saveBtn.className = "btn btn-success flex-grow-1";
        saveBtn.textContent = "💾 Save";

        const cancelBtn = document.createElement("button");
        cancelBtn.id = "cancel-edit-btn";
        cancelBtn.className = "btn btn-secondary flex-grow-1";
        cancelBtn.textContent = "✖ Cancel";

        commentSubmit.classList.add("d-none")
        editActionsContainer.append(saveBtn, cancelBtn);

        saveBtn.addEventListener("click", saveEdit);
        cancelBtn.addEventListener("click", cancelEdit);
    }

    async function saveEdit(e) {
        e.preventDefault();

        const newContent = textarea.value.trim();
        if (!newContent) {
            alert("Empty comment not allowed");
            return;
        }

        const res = await fetch(`/posts/comment/${editingCommentId}/edit/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
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
        const commentSubmit = document.querySelector(".comment-sumbmit")
        editingCommentId = null;
        textarea.value = "";
        submitBtn.style.display = "block";

        document.getElementById("save-edit-btn")?.remove();
        document.getElementById("cancel-edit-btn")?.remove();
        commentSubmit.classList.remove("d-none")
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
    
    initTaggedPeopletoggle();
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

function initTaggedPeopletoggle() {
    const PEOPLE_TO_SHOW = 3;

    document.querySelectorAll('.tagged-people-container').forEach(container => {
        const tags = Array.from(container.querySelectorAll('.tagged-people-item'));
        const showBtn = container.querySelector('.show-more-tagged-people');
        const hideBtn = container.querySelector('.hide-tagged-people');

        if (!showBtn || !hideBtn || tags.length <= PEOPLE_TO_SHOW) return;

        let visibleCount = PEOPLE_TO_SHOW;

        tags.forEach((tag, i) => {
            tag.style.display = i < PEOPLE_TO_SHOW ? 'inline-block' : 'none';
        });

        showBtn.addEventListener('click', () => {
            visibleCount += PEOPLE_TO_SHOW;

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
            visibleCount = PEOPLE_TO_SHOW;

            tags.forEach((tag, i) => {
                tag.style.display = i < PEOPLE_TO_SHOW ? 'inline-block' : 'none';
            });

            hideBtn.style.display = 'none';
            showBtn.style.display = 'inline-block';
        });
    });
}
