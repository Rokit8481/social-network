console.log("🔥 infinite_scroll.js loaded");
window.addEventListener("scroll", () => {
    console.log("scroll event");
});

let loading = false;
let hasMore = true;

window.addEventListener("scroll", () => {
    if (loading || !hasMore) return;

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
        loadMorePosts();
    }
});

function loadMorePosts() {
    if (loading) return;
    loading = true;
    document.getElementById("loader").classList.remove("d-none");
    document.getElementById("end-of-posts").classList.remove("d-none");

    const posts = document.querySelectorAll(".post-item");
    if (!posts.length) return;

    const lastId = posts[posts.length - 1].dataset.postId;

    fetch(`/posts/infinite/?last_id=${lastId}`)
        .then(r => r.json())
        .then(data => {
            document
                .getElementById("posts-container")
                .insertAdjacentHTML("beforeend", data.html);

            hasMore = data.has_more;
            loading = false;

            document.getElementById("loader").classList.add("d-none");

            initLikeButtons();
        });
}

function initLikeButtons() {
    document.querySelectorAll(".like-btn").forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = "1";

        btn.addEventListener("click", () => {
            console.log(`Button was clickes (infinite.js)`)
            const postId = btn.dataset.postId;
            const counter = btn.querySelector(".likes-count");

            fetch(`/posts/api/post/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(r => r.json())
            .then(data => {
                counter.textContent = data.likes_count;
                console.log(`Likes count reset to ${counter.textContent}`)
            });
        });
    });
}

document.addEventListener("DOMContentLoaded", initLikeButtons);