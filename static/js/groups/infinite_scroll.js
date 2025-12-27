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

    const groups = document.querySelectorAll(".group-item");
    if (!groups.length) {
        loading = false;
        return;
    }

    const lastId = groups[groups.length - 1].dataset.groupId;

    const params = new URLSearchParams(window.location.search);
    params.set("last_id", lastId);

    fetch(`/groups/infinite/?${params.toString()}`)
        .then(r => r.json())
        .then(data => {
            document
                .getElementById("group-container")
                .insertAdjacentHTML("beforeend", data.html);

            hasMore = data.has_more;
            loading = false;

            document.getElementById("loader").classList.add("d-none");

            if (!hasMore) {
                document.getElementById("end-of-groups").classList.remove("d-none");
            }
        });
}
