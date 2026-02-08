let loading = false;
let hasMore = true;
let hasScrolledToHash = false;

const container = document.getElementById("board-messages-container");
const messagesList = document.getElementById("messages-list");
const loader = document.getElementById("loader");
const endBlock = document.getElementById("end-of-board-messages");

const boardSlug = container.dataset.boardSlug;
const scrollBox = container.closest(".board-messages");

function tryScrollToHash() {
    if (!window.location.hash) return false;
    if (hasScrolledToHash) return false; 

    const targetId = window.location.hash.substring(1);
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('highlighted');

        setTimeout(() => {
            targetElement.classList.remove('highlighted');
        }, 7500);

        hasScrolledToHash = true; 
        return true;
    }
    return false;
}

document.addEventListener('DOMContentLoaded', () => {
    tryScrollToHash();
});

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

    const messages = container.querySelectorAll(".board-message-item");
    if (!messages.length) {
        loading = false;
        return;
    }

    const lastId = messages[messages.length - 1].dataset.id;

    fetch(`/boards/${boardSlug}/infinite/?last_id=${lastId}`)
        .then(res => res.json())
        .then(data => {
            messagesList.insertAdjacentHTML("beforeend", data.html);

            hasMore = data.has_more;
            loading = false;
            loader.classList.add("d-none");

            if (!hasMore) {
                endBlock.classList.remove("d-none");
            }

            // Спроба скролу після підвантаження — тільки якщо ще не робили
            if (!hasScrolledToHash) {
                tryScrollToHash();
            }
        })
        .catch(() => {
            loading = false;
            loader.classList.add("d-none");
        });
}