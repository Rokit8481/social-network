export function initInfiniteComments(container) {
    let loading = false;
    let hasMore = true;

    const commentsList = container.querySelector("#comments-list");
    const loader = document.getElementById("comments-loader");
    const endBlock = document.getElementById("comments-end");
    const url = container.dataset.url;

    container.addEventListener("scroll", () => {
        if (loading || !hasMore) return;

        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
            loadMore();
        }
    });

    function loadMore() {
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
                scrollToHashIfNeeded();
                hasMore = data.has_more;

                if (!hasMore) endBlock.classList.remove("d-none");
            })
            .finally(() => {
                loader.classList.add("d-none");
                loading = false;
            });
    }
}

function scrollToHashIfNeeded() {
    if (!window.location.hash) return;

    const targetId = window.location.hash.substring(1);
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('highlighted');
        setTimeout(() => targetElement.classList.remove('highlighted'), 7500);
    }
}