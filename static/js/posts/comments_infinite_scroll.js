let loading = false;
let hasMore = true;

const container = document.getElementById("comments-box");
const commentsList = document.getElementById("comments-list");
const loader = document.getElementById("comments-loader");
const endBlock = document.getElementById("comments-end");

const scrollBox = container;
const url = container.dataset.url;

scrollBox.addEventListener("scroll", () => {
    if (loading || !hasMore) return;

    if (scrollBox.scrollTop + scrollBox.clientHeight >= scrollBox.scrollHeight - 100) {
        loadMoreComments();
    }
});

function loadMoreComments() {
    loading = true;
    loader.classList.remove("d-none");

    const comments = container.querySelectorAll(".comment-item");
    const lastId = comments.length
        ? comments[comments.length - 1].dataset.commentId
        : null;

    fetch(`${url}?last_id=${lastId}`)
        .then(res => res.json())
        .then(data => {
            commentsList.insertAdjacentHTML("beforeend", data.html);
            hasMore = data.has_more;

            if (!hasMore) {
                endBlock.classList.remove("d-none");
            }
        })
        .catch(console.error)
        .finally(() => {
            loader.classList.add("d-none");
            loading = false;
        });
}
