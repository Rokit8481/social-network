document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.onclick = () => {
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
        };
    });

    document.querySelectorAll(".like-comment-btn").forEach(btn => {
        btn.onclick = () => {
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
        };
    });
});