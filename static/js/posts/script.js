document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const postId = btn.dataset.postId;
            const likesCountSpan = btn.querySelector(".likes-count");

            fetch(`/posts/api/post/like/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": CSRF_TOKEN,
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                likesCountSpan.textContent = data.likes_count;
            });
        });
    });

    document.querySelectorAll(".media-item").forEach(item => {
        item.addEventListener("click", () => {
            const index = item.dataset.index;
            const carousel = document.querySelector(
                item.dataset.bsTarget + " .carousel"
            );
            bootstrap.Carousel.getOrCreateInstance(carousel).to(index);
        });
    });
    
    initTaggedPeopletoggle();
});

function initTaggedPeopletoggle() {
    const PEOPLE_TO_SHOW = 3;

    document.querySelectorAll('.tagged-people-container').forEach(container => {
        const tags = Array.from(container.querySelectorAll('.tagged-people-item'));
        const showBtn = container.querySelector('.show-more-tagged-people');
        const hideBtn = container.querySelector('.hide-tagged-people');

        if (!showBtn || !hideBtn || tags.length <= PEOPLE_TO_SHOW) return;

        let visibleCount = PEOPLE_TO_SHOW;

        tags.forEach((tag, i) => {
            tag.style.display = i < PEOPLE_TO_SHOW ? 'inline-block' : 'none';
        });

        showBtn.addEventListener('click', () => {
            visibleCount += PEOPLE_TO_SHOW;

            tags.forEach((tag, i) => {
                if (i < visibleCount) {
                    tag.style.display = 'inline-block';
                }
            });

            hideBtn.style.display = 'inline-block';

            if (visibleCount >= tags.length) {
                showBtn.style.display = 'none';
            }
        });

        hideBtn.addEventListener('click', () => {
            visibleCount = PEOPLE_TO_SHOW;

            tags.forEach((tag, i) => {
                tag.style.display = i < PEOPLE_TO_SHOW ? 'inline-block' : 'none';
            });

            hideBtn.style.display = 'none';
            showBtn.style.display = 'inline-block';
        });
    });
}
