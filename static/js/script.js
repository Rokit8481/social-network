document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".like-btn");

    buttons.forEach(btn => {
        btn.onclick = () => {
            const postId = btn.dataset.postId;
            const likesCountSpan = btn.querySelector(".likes-count");
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/posts/api/like/${postId}/`, {
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
        }
    });
});
