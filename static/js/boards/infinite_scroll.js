let loading = false;
let hasMore = true;

window.addEventListener("scroll", () => {
    if (loading || !hasMore) return;

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
        loadMorePosts();
    }
});

function loadMorePosts() {
    loading = true;
    document.getElementById("loader").classList.remove("d-none");

    const boards = document.querySelectorAll(".board-item");
    if (!boards.length) {
        loading = false;
        return;
    }

    const lastId = boards[boards.length - 1].dataset.boardId;

    const params = new URLSearchParams(window.location.search);
    params.set("last_id", lastId);

    fetch(`/boards/infinite/?${params.toString()}`)
        .then(r => r.json())
        .then(data => {
            document
                .getElementById("board-container")
                .insertAdjacentHTML("beforeend", data.html);

            hasMore = data.has_more;
            loading = false;

            document.getElementById("loader").classList.add("d-none");

            if (!hasMore) {
                document.getElementById("end-of-boards").classList.remove("d-none");
            }
        });
}
