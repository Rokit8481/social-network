let loading = false;
let hasMore = true;

const container = document.getElementById("group-messages-container");
const messagesList = document.getElementById("messages-list");
const loader = document.getElementById("loader");
const endBlock = document.getElementById("end-of-group-messages");

const groupSlug = container.dataset.groupSlug;
const scrollBox = container.closest(".group-messages");

scrollBox.addEventListener("scroll", () => {
    if (loading || !hasMore) return;

    const threshold = 100;

    if (
        scrollBox.scrollTop + scrollBox.clientHeight
        >= scrollBox.scrollHeight - threshold
    ) {
        loadMoreMessages();
    }
});


function loadMoreMessages() {
    loading = true;
    loader.classList.remove("d-none");

    const messages = container.querySelectorAll(".group-message-item");
    if (!messages.length) {
        loading = false;
        return;
    }

    const lastId = messages[messages.length - 1].dataset.postId;

    fetch(`/groups/${groupSlug}/infinite/?last_id=${lastId}`)
        .then(res => res.json())
        .then(data => {
            messagesList.insertAdjacentHTML("beforeend", data.html);

            hasMore = data.has_more;
            loading = false;
            loader.classList.add("d-none");

            if (!hasMore) {
                endBlock.classList.remove("d-none");
            }
        })
        .catch(() => {
            loading = false;
            loader.classList.add("d-none");
        });
}

