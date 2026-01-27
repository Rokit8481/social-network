export function initCommentLikes(container) {
    container.addEventListener("click", e => {
        const btn = e.target.closest(".like-comment-btn");
        if (!btn) return;

        const commentId = btn.dataset.commentId;
        const countSpan = btn.querySelector(".comment-likes-count");

        fetch(`/posts/api/comment/like/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            countSpan.textContent = data.likes_count;
        });
    });
};
